from __future__ import annotations

import math
from typing import Callable, Tuple
import pygame

from core.ICs import IC, Pin
from core.manager import Manager
from ui.ui_element import UiElement

ColorTuple = Tuple[int, int, int]


class IC_Element(UiElement):
    """
    Visual representation of a real-life Integrated Circuit (IC) chip.
    Modeled after the classic Dual In-line Package (DIP-14) standard:
    - 7 pins on the left side (Pins 1..7 from top to bottom)
    - 7 pins on the right side (Pins 14..8 from top to bottom)
    - Realistic epoxy body with orientation notch, pin 1 dot, and laser silk-screen
    - Metallic leads with interactive pin terminal nodes
    - Real-time logic level indicators and pinouts matching physical datasheets
    """

    PIN_RADIUS = 10
    PIN_LEAD_LENGTH = 18
    PIN_PITCH = 36  # Vertical distance between pins

    def __init__(
        self,
        x: int,
        y: int,
        ic: IC,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        on_delete: Callable[["IC_Element"], None] | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.ic = ic
        self.font = font
        self.small_font = small_font
        self.on_delete = on_delete

        self.pins_per_side = max(1, self.ic.total_pins // 2)
        self.width = 180
        # Header (52px) + pins spacing + footer (24px)
        self.height = 52 + self.pins_per_side * self.PIN_PITCH + 20

        self.is_dragging: bool = False
        self.drag_offset_x: int = 0
        self.drag_offset_y: int = 0

        self.is_hovered: bool = False
        self.hovered_pin: dict | None = None
        self.delete_hovered: bool = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def delete_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x + self.width - 24, self.y + 6, 18, 18)

    def get_pin_side(self, pin_number: int) -> str:
        """Determine whether a pin is on the 'left' or 'right' side of the DIP package."""
        if pin_number <= self.pins_per_side:
            return "left"
        return "right"

    def get_pin_pos(self, pin_number: int) -> tuple[int, int]:
        """
        Get absolute screen (x, y) coordinates for the terminal pad of a pin.
        In standard DIP packages:
        - Pins 1..N/2 go DOWN the left side (row 0 to pins_per_side - 1)
        - Pins N/2+1..N go UP the right side:
          Pin N (e.g. 14) is at the top right (row 0), opposite Pin 1!
          Pin N/2+1 (e.g. 8) is at the bottom right, opposite Pin 7!
        """
        if pin_number <= self.pins_per_side:
            row = pin_number - 1
            px = self.x - self.PIN_LEAD_LENGTH
        else:
            row = self.ic.total_pins - pin_number
            px = self.x + self.width + self.PIN_LEAD_LENGTH

        py = self.y + 54 + row * self.PIN_PITCH
        return (px, py)

    def get_input_pin_pos(self, index: int) -> tuple[int, int]:
        """Backwards compatibility helper: position of the i-th input pin."""
        if index < len(self.ic.input_pins):
            return self.get_pin_pos(self.ic.input_pins[index].number)
        py = self.y + 54 + index * self.PIN_PITCH
        return (self.x - self.PIN_LEAD_LENGTH, py)

    def get_output_pin_pos(self, index: int) -> tuple[int, int]:
        """Backwards compatibility helper: position of the j-th output pin."""
        if index < len(self.ic.output_pins):
            return self.get_pin_pos(self.ic.output_pins[index].number)
        py = self.y + 54 + index * self.PIN_PITCH
        return (self.x + self.width + self.PIN_LEAD_LENGTH, py)

    def get_pin_at_pos(self, pos: tuple[int, int]) -> dict | None:
        """Check if a mouse position hits any pin terminal on this IC."""
        px, py = pos
        for pin_num, pin in self.ic.pins.items():
            tx, ty = self.get_pin_pos(pin_num)
            if math.hypot(px - tx, py - ty) <= self.PIN_RADIUS + 4:
                is_conn = (
                    Manager.is_input_connected(pin.node_id)
                    if pin.is_input
                    else (len(Manager.get_connected_inputs(pin.node_id)) > 0)
                )
                return {
                    "type": pin.pin_type,
                    "index": pin_num - 1,
                    "pin_number": pin_num,
                    "pin_name": pin.name,
                    "node_id": pin.node_id,
                    "pos": (tx, ty),
                    "side": self.get_pin_side(pin_num),
                    "connected": is_conn,
                    "value": Manager.node_values.get(pin.node_id, pin.value),
                    "ic_element": self,
                    "pin": pin,
                }
        return None

    def event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            pos = getattr(event, "pos", (0, 0))
            self.is_hovered = self.rect.collidepoint(pos)
            self.delete_hovered = self.delete_rect.collidepoint(pos)
            self.hovered_pin = self.get_pin_at_pos(pos)

            if self.is_dragging:
                self.x = pos[0] - self.drag_offset_x
                self.y = pos[1] - self.drag_offset_y
                # Keep within screen boundaries
                self.x = max(24, min(1280 - self.width - 24, self.x))
                self.y = max(56, min(720 - self.height - 20, self.y))

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

    def render(self, surface: pygame.Surface) -> None:
        lead_color = (165, 175, 190)
        lead_highlight = (220, 230, 245)

        # 1. Draw metallic DIP leads extending horizontally
        for pin_num in range(1, self.ic.total_pins + 1):
            pin_x, pin_y = self.get_pin_pos(pin_num)
            side = self.get_pin_side(pin_num)
            body_x = self.x if side == "left" else self.x + self.width

            # Metal lead shadow / body
            pygame.draw.line(surface, lead_color, (body_x, pin_y), (pin_x, pin_y), 4)
            pygame.draw.line(surface, lead_highlight, (body_x, pin_y - 1), (pin_x, pin_y - 1), 1)

        # 2. Draw IC main body (DIP package casing)
        body_bg: ColorTuple = (24, 27, 34)
        border_color: ColorTuple = (65, 75, 92)
        if self.is_dragging:
            border_color = (96, 165, 250)
        elif self.is_hovered:
            border_color = (80, 92, 110)

        # Drop shadow
        shadow_rect = pygame.Rect(self.x + 4, self.y + 5, self.width, self.height)
        pygame.draw.rect(surface, (12, 14, 18), shadow_rect, border_radius=8)

        # Molded epoxy package
        pygame.draw.rect(surface, body_bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        # Top notch (classic DIP orientation indentation)
        notch_center = (self.x + self.width // 2, self.y)
        pygame.draw.circle(surface, (14, 16, 22), notch_center, 9)
        pygame.draw.circle(surface, border_color, notch_center, 9, width=2)

        # Pin 1 circular dimple index dot (top-left)
        p1_dot_center = (self.x + 18, self.y + 16)
        pygame.draw.circle(surface, (15, 17, 23), p1_dot_center, 5)
        pygame.draw.circle(surface, (50, 60, 75), p1_dot_center, 5, width=1)

        # 3. IC Silk-screen markings (Laser-etched technical lettering)
        brand_surf = self.small_font.render("LOGIC LAB", True, (100, 116, 139))
        surface.blit(brand_surf, brand_surf.get_rect(center=(self.x + self.width // 2, self.y + 16)))

        # Full part number (e.g. SN7404N)
        part_no = f"SN{self.ic.name}N" if not self.ic.name.startswith("SN") else self.ic.name
        title_surf = self.font.render(part_no, True, (241, 245, 249))
        surface.blit(title_surf, title_surf.get_rect(center=(self.x + self.width // 2, self.y + 32)))

        # Subtitle type
        type_surf = self.small_font.render(self.ic.type_name, True, (148, 163, 184))
        surface.blit(type_surf, type_surf.get_rect(center=(self.x + self.width // 2, self.y + 46)))

        # Lot code stamp vertically or near bottom
        lot_surf = self.small_font.render("MALAYSIA  2418B", True, (71, 85, 105))
        surface.blit(lot_surf, lot_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height - 12)))

        # 4. Delete [X] button
        del_bg = (239, 68, 68) if self.delete_hovered else (40, 48, 62)
        del_fg = (255, 255, 255) if self.delete_hovered else (156, 163, 175)
        pygame.draw.rect(surface, del_bg, self.delete_rect, border_radius=4)
        x_surf = self.small_font.render("×", True, del_fg)
        surface.blit(x_surf, x_surf.get_rect(center=self.delete_rect.center))

        # 5. Draw Pins, Pin Labels, and Interactive Terminal Pads
        for pin_num, pin in self.ic.pins.items():
            pin_x, pin_y = self.get_pin_pos(pin_num)
            side = self.get_pin_side(pin_num)
            val = Manager.node_values.get(pin.node_id, pin.value)
            is_connected = Manager.is_input_connected(pin.node_id) if pin.is_input else False
            is_pin_hovered = (
                self.hovered_pin is not None and self.hovered_pin["pin_number"] == pin_num
            )

            # Pin Number & Name printed on package body
            num_surf = self.small_font.render(str(pin_num), True, (115, 125, 145))
            if pin.is_vcc:
                name_col = (248, 113, 113)  # Red for VCC
            elif pin.is_gnd:
                name_col = (148, 163, 184)  # Slate for GND
            elif pin.is_output:
                name_col = (96, 165, 250)   # Blue for outputs
            else:
                name_col = (226, 232, 240)  # Light for inputs

            name_surf = self.small_font.render(pin.name, True, name_col)

            if side == "left":
                # Number near outer left, name slightly inward
                surface.blit(num_surf, (self.x + 6, pin_y - 7))
                surface.blit(name_surf, (self.x + 22, pin_y - 7))
            else:
                # Name slightly inward, number near outer right
                name_rect = name_surf.get_rect(right=self.x + self.width - 22, centery=pin_y)
                num_rect = num_surf.get_rect(right=self.x + self.width - 6, centery=pin_y)
                surface.blit(name_surf, name_rect)
                surface.blit(num_surf, num_rect)

            # Pin Terminal Node (Solder pad / Probe terminal)
            if val == 1:
                node_bg = (34, 197, 94)  # HIGH: Vibrant Green
                text_col = (10, 35, 15)
                ring_col = (74, 222, 128)
            else:
                node_bg = (51, 65, 85)   # LOW: Dark Slate
                text_col = (203, 213, 225)
                ring_col = (100, 116, 139)

            if pin.is_vcc:
                ring_col = (239, 68, 68)  # Distinct red ring for VCC
            elif pin.is_gnd:
                ring_col = (100, 116, 139) # Ground ring

            # Hover highlight ring
            if is_pin_hovered:
                pygame.draw.circle(
                    surface,
                    (250, 204, 21) if (pin.is_input and not is_connected) else (147, 197, 253),
                    (pin_x, pin_y),
                    self.PIN_RADIUS + 3,
                    width=2,
                )

            # Draw circle pad
            pygame.draw.circle(surface, node_bg, (pin_x, pin_y), self.PIN_RADIUS)
            pygame.draw.circle(surface, ring_col, (pin_x, pin_y), self.PIN_RADIUS, width=2)

            # Logic level text "0" or "1"
            txt_surf = self.small_font.render(str(val), True, text_col)
            surface.blit(txt_surf, txt_surf.get_rect(center=(pin_x, pin_y)))

            # If unconnected input: show small outer hint that it's toggleable
            if pin.is_input and not is_connected:
                pygame.draw.circle(
                    surface,
                    (234, 179, 8) if is_pin_hovered else (120, 140, 170),
                    (pin_x, pin_y),
                    self.PIN_RADIUS + 1,
                    width=1,
                )
