from __future__ import annotations

import math
from typing import Callable, Type
import pygame

from core.ICs import IC, IC7404, IC7408, IC7432, Pin
from core.manager import Manager
from ui.elements.ic import IC_Element
from ui.elements.wire import Wire, get_bezier_curve_points
from ui.ui_element import UiElement


class CircuitCanvas(UiElement):
    """Interactive canvas managing real-life IC elements, wires, and circuit interactions."""

    def __init__(
        self,
        width: int,
        height: int,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.font = font
        self.small_font = small_font
        self.status_callback = status_callback

        self.ic_elements: list[IC_Element] = []
        self.wires: list[Wire] = []

        # Interactive wiring state
        self.wiring_source: dict | None = None
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.hovered_wire: Wire | None = None
        self.hovered_pin: dict | None = None

        # Position offset counter for adding new ICs nicely
        self.spawn_offset = 0

    def set_status(self, message: str) -> None:
        if self.status_callback is not None:
            self.status_callback(message)

    def add_ic(
        self, ic_cls: Type[IC], pos: tuple[int, int] | None = None
    ) -> IC_Element:
        """Instantiate an IC class, register its UI element, and position it."""
        ic_instance = ic_cls()

        if pos is None:
            # Staggered placement around board
            base_x = 160 + (self.spawn_offset % 3) * 260
            base_y = 100 + ((self.spawn_offset // 3) % 2) * 160
            self.spawn_offset += 1
            pos = (base_x, base_y)

        elem = IC_Element(
            x=pos[0],
            y=pos[1],
            ic=ic_instance,
            font=self.font,
            small_font=self.small_font,
            on_delete=self.remove_ic,
        )
        self.ic_elements.append(elem)
        self.set_status(f"Added {ic_instance.name} ({ic_instance.type_name}) to circuit board")
        return elem

    def remove_ic(self, ic_elem: IC_Element) -> None:
        """Remove an IC element, unregister its nodes, and delete attached wires."""
        if ic_elem in self.ic_elements:
            self.ic_elements.remove(ic_elem)

        # Unregister from backend manager
        Manager.unregister_ic(ic_elem.ic)

        # Remove all wires connected to any pin of this IC
        all_nodes = set(ic_elem.ic.input_nodes + ic_elem.ic.output_nodes)
        if hasattr(ic_elem.ic, "pins"):
            for p in ic_elem.ic.pins.values():
                all_nodes.add(p.node_id)

        self.wires = [
            w
            for w in self.wires
            if w.input_node not in all_nodes and w.output_node not in all_nodes
        ]
        self.set_status(f"Removed {ic_elem.ic.name} and disconnected attached wires")

    def clear_all(self) -> None:
        """Clear all ICs and wires from canvas and reset Manager."""
        self.ic_elements.clear()
        self.wires.clear()
        self.wiring_source = None
        self.spawn_offset = 0
        Manager.reset()
        self.set_status("Circuit board cleared")

    def find_pin_info(self, node_id: int) -> tuple[IC_Element, Pin] | None:
        """Find the IC element and Pin object for a given node ID."""
        for elem in self.ic_elements:
            if hasattr(elem.ic, "pins"):
                for pin in elem.ic.pins.values():
                    if pin.node_id == node_id:
                        return (elem, pin)
            else:
                # Fallback for synthetic pins
                for pin in elem.ic.input_pins + elem.ic.output_pins:
                    if pin.node_id == node_id:
                        return (elem, pin)
        return None

    def connect_pins(self, output_node: int, input_node: int) -> bool:
        """Connect an output/source node to an input node both visually and in Manager."""
        # 1. Disconnect any existing wire to this input node
        self.disconnect_pin(input_node)

        # 2. Inform manager backend
        Manager.connect(input_node, output_node)

        # 3. Create visual wire
        src_info = self.find_pin_info(output_node)
        tgt_info = self.find_pin_info(input_node)

        if not src_info or not tgt_info:
            return False

        src_elem, src_pin = src_info
        tgt_elem, tgt_pin = tgt_info

        wire = Wire(
            output_node=output_node,
            input_node=input_node,
            get_start_pos=lambda: src_elem.get_pin_pos(src_pin.number),
            get_end_pos=lambda: tgt_elem.get_pin_pos(tgt_pin.number),
            get_start_side=lambda: src_elem.get_pin_side(src_pin.number),
            get_end_side=lambda: tgt_elem.get_pin_side(tgt_pin.number),
        )
        self.wires.append(wire)
        self.set_status(
            f"Connected {src_elem.ic.name} Pin {src_pin.number} ({src_pin.name}) -> {tgt_elem.ic.name} Pin {tgt_pin.number} ({tgt_pin.name})"
        )
        return True

    def disconnect_pin(self, input_node: int) -> bool:
        """Disconnect an input pin visually and in Manager."""
        Manager.disconnect(input_node)
        initial_len = len(self.wires)
        self.wires = [w for w in self.wires if w.input_node != input_node]
        if len(self.wires) < initial_len:
            self.set_status(f"Disconnected wire from input node {input_node}")
            return True
        return False

    def get_pin_at_pos(self, pos: tuple[int, int]) -> dict | None:
        """Check all IC elements to see if pos hits any pin terminal pad."""
        for elem in reversed(self.ic_elements):
            pin = elem.get_pin_at_pos(pos)
            if pin is not None:
                return pin
        return None

    def event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = getattr(event, "pos", (0, 0))
            self.hovered_pin = self.get_pin_at_pos(self.mouse_pos)

            # Check wire hover
            self.hovered_wire = None
            if self.hovered_pin is None and not self.wiring_source:
                for wire in reversed(self.wires):
                    if wire.is_near_pos(self.mouse_pos):
                        self.hovered_wire = wire
                        wire.is_hovered = True
                        break
                    else:
                        wire.is_hovered = False

            # Update status message on hover
            if self.wiring_source:
                src_pin = self.wiring_source["pin"]
                src_ic = self.wiring_source["ic_element"].ic
                self.set_status(
                    f"Wiring from {src_ic.name} Pin {src_pin.number} ({src_pin.name})... Release on input pin to connect"
                )
            elif self.hovered_pin:
                p_type = self.hovered_pin["type"]
                p_num = self.hovered_pin["pin_number"]
                p_name = self.hovered_pin["pin_name"]
                p_val = self.hovered_pin["value"]
                is_conn = self.hovered_pin["connected"]
                ic_name = self.hovered_pin["ic_element"].ic.name
                desc = self.hovered_pin["pin"].description or p_name

                if p_type == "input":
                    if is_conn:
                        self.set_status(
                            f"{ic_name} Pin {p_num} ({p_name}): {desc} = {p_val} [CONNECTED: driven by IC output. Right-click to disconnect]"
                        )
                    else:
                        self.set_status(
                            f"{ic_name} Pin {p_num} ({p_name}): {desc} = {p_val} [UNCONNECTED: Click to toggle 0/1, Drag to connect]"
                        )
                elif p_type in ("vcc", "gnd"):
                    self.set_status(
                        f"{ic_name} Pin {p_num} ({p_name}): {desc} = {p_val} [Power Pin: Drag to supply constant {'HIGH (+5V)' if p_val else 'LOW (0V)'}]"
                    )
                else:
                    self.set_status(
                        f"{ic_name} Pin {p_num} ({p_name}): {desc} = {p_val} [Output: Drag to wire to an input pin]"
                    )
            elif self.hovered_wire:
                self.set_status(
                    f"Wire Node {self.hovered_wire.output_node} -> Node {self.hovered_wire.input_node} [Right-click to delete wire]"
                )

            # Forward mouse motion to IC elements for dragging
            for elem in self.ic_elements:
                elem.event(event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = getattr(event, "pos", (0, 0))
            button = getattr(event, "button", 1)

            if button == 1:  # Left Click
                # 1. Check delete button on ICs
                for elem in reversed(self.ic_elements):
                    if elem.delete_rect.collidepoint(pos):
                        self.remove_ic(elem)
                        return

                # 2. Check if clicked a pin
                clicked_pin = self.get_pin_at_pos(pos)
                if clicked_pin is not None:
                    pin_type = clicked_pin["type"]
                    node_id = clicked_pin["node_id"]
                    is_connected = clicked_pin["connected"]

                    # If unconnected input or power pin: toggle it!
                    if pin_type in ("input", "vcc", "gnd") and not is_connected:
                        new_val = Manager.toggle_input(node_id)
                        ic_name = clicked_pin["ic_element"].ic.name
                        p_name = clicked_pin["pin_name"]
                        self.set_status(
                            f"Toggled {ic_name} Pin ({p_name}) to {new_val}"
                        )

                    # Also initiate wire dragging from this pin
                    self.wiring_source = clicked_pin
                    return

                # 3. Check if clicked an IC body to drag
                for elem in reversed(self.ic_elements):
                    if elem.rect.collidepoint(pos):
                        # Bring clicked IC to front
                        self.ic_elements.remove(elem)
                        self.ic_elements.append(elem)

                        elem.is_dragging = True
                        elem.drag_offset_x = pos[0] - elem.x
                        elem.drag_offset_y = pos[1] - elem.y
                        return

            elif button == 3:  # Right Click (Disconnect / Delete Wire)
                # Check if right-clicked on an input pin: disconnect it
                clicked_pin = self.get_pin_at_pos(pos)
                if clicked_pin is not None:
                    node_id = clicked_pin["node_id"]
                    if clicked_pin["type"] == "input":
                        self.disconnect_pin(node_id)
                    else:
                        # Output or power pin: disconnect all wires driven by it
                        inputs = Manager.get_connected_inputs(node_id)
                        for inp in inputs:
                            self.disconnect_pin(inp)
                    return

                # Check if right-clicked on a wire
                for wire in list(self.wires):
                    if wire.is_near_pos(pos):
                        self.disconnect_pin(wire.input_node)
                        return

        elif event.type == pygame.MOUSEBUTTONUP:
            button = getattr(event, "button", 1)
            if button == 1:
                # If we were dragging a wire, check where it dropped
                if self.wiring_source is not None:
                    target_pin = self.get_pin_at_pos(self.mouse_pos)
                    if target_pin is not None:
                        src_type = self.wiring_source["type"]
                        tgt_type = target_pin["type"]
                        src_node = self.wiring_source["node_id"]
                        tgt_node = target_pin["node_id"]

                        # Valid connection if one is driving (output, vcc, gnd) and one is receiving (input)
                        if src_type in ("output", "vcc", "gnd") and tgt_type == "input":
                            self.connect_pins(src_node, tgt_node)
                        elif src_type == "input" and tgt_type in ("output", "vcc", "gnd"):
                            self.connect_pins(tgt_node, src_node)

                    self.wiring_source = None

                # Release all dragging ICs
                for elem in self.ic_elements:
                    elem.event(event)

    def update(self):
        for elem in self.ic_elements:
            elem.update()

    def render(self, surface: pygame.Surface):
        # 1. Background grid pattern (subtle PCB / breadboard dots)
        dot_color = (46, 52, 64)
        grid_step = 28
        for x in range(grid_step, self.width, grid_step):
            for y in range(54 + grid_step, self.height, grid_step):
                surface.set_at((x, y), dot_color)

        # 2. Render all established wires
        for wire in self.wires:
            wire.render(surface)

        # 3. Render in-progress wire being dragged
        if self.wiring_source is not None:
            start_pos = self.wiring_source["pos"]
            end_pos = self.mouse_pos
            start_side = self.wiring_source.get("side", "right")

            target = self.get_pin_at_pos(self.mouse_pos)
            end_side = target.get("side", "left") if target else ("left" if end_pos[0] > start_pos[0] else "right")

            points = get_bezier_curve_points(start_pos, end_pos, start_side=start_side, end_side=end_side)

            val = self.wiring_source["value"]
            preview_color = (34, 197, 94) if val == 1 else (148, 163, 184)

            # Draw glowing line to cursor
            if len(points) >= 2:
                pygame.draw.lines(surface, preview_color, False, points, 3)

            # Highlight target pin if mouse hovers over a valid opposite pin
            if target and target["type"] != self.wiring_source["type"]:
                tx, ty = target["pos"]
                pygame.draw.circle(surface, (250, 204, 21), (tx, ty), 14, width=3)

        # 4. Render all IC elements
        for elem in self.ic_elements:
            elem.render(surface)
