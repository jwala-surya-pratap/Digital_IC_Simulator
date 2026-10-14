from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ICs import IC


class Manager:
    node_relations: dict[int, int] = {}  # input_node -> output_node
    node_values: dict[int, int] = {}  # node_id -> logic level (0 or 1)
    counter: int = 0

    ics: list[IC] = []
    node_to_ic: dict[int, tuple[IC, str, int]] = {}  # node_id -> (ic, "input"|"output"|"vcc"|"gnd", pin_or_index)

    @classmethod
    def reset(cls) -> None:
        """Reset all manager state (useful for tests and canvas clearing)."""
        cls.node_relations.clear()
        cls.node_values.clear()
        cls.counter = 0
        cls.ics.clear()
        cls.node_to_ic.clear()

    @classmethod
    def get_nodes(
        cls, input_count: int, output_count: int
    ) -> tuple[list[int], list[int]]:
        input_nodes: list[int] = []
        for _ in range(input_count):
            cls.counter += 1
            input_nodes.append(cls.counter)
            cls.node_values[cls.counter] = 0

        output_nodes: list[int] = []
        for _ in range(output_count):
            cls.counter += 1
            output_nodes.append(cls.counter)
            cls.node_values[cls.counter] = 0

        return (input_nodes, output_nodes)

    @classmethod
    def register_ic(cls, ic: IC) -> None:
        """Register an IC with the manager and index its nodes."""
        if ic not in cls.ics:
            cls.ics.append(ic)

        # Register input nodes
        for i, node_id in enumerate(ic.input_nodes):
            cls.node_to_ic[node_id] = (ic, "input", i)
            if node_id not in cls.node_values:
                cls.node_values[node_id] = 0

        # Register output nodes
        for j, node_id in enumerate(ic.output_nodes):
            cls.node_to_ic[node_id] = (ic, "output", j)
            if node_id not in cls.node_values:
                cls.node_values[node_id] = 0

        # Register VCC and GND pins if present
        if hasattr(ic, "vcc_pin") and ic.vcc_pin is not None:
            v_id = ic.vcc_pin.node_id
            cls.node_to_ic[v_id] = (ic, "vcc", ic.vcc_pin.number)
            if v_id not in cls.node_values:
                cls.node_values[v_id] = 1

        if hasattr(ic, "gnd_pin") and ic.gnd_pin is not None:
            g_id = ic.gnd_pin.node_id
            cls.node_to_ic[g_id] = (ic, "gnd", ic.gnd_pin.number)
            if g_id not in cls.node_values:
                cls.node_values[g_id] = 0

        cls.update_simulation()

    @classmethod
    def unregister_ic(cls, ic: IC) -> None:
        """Unregister an IC and remove all its connections and nodes."""
        if ic in cls.ics:
            cls.ics.remove(ic)

        all_node_ids = set(ic.input_nodes + ic.output_nodes)
        if hasattr(ic, "pins"):
            for p in ic.pins.values():
                all_node_ids.add(p.node_id)

        # Remove connections where this IC's inputs are targets
        for node_id in all_node_ids:
            cls.node_relations.pop(node_id, None)
            cls.node_values.pop(node_id, None)
            cls.node_to_ic.pop(node_id, None)

        # Remove connections where this IC's outputs/power pins are sources
        to_disconnect = [
            inp for inp, out in cls.node_relations.items() if out in all_node_ids
        ]
        for inp in to_disconnect:
            cls.node_relations.pop(inp, None)

        cls.update_simulation()

    @classmethod
    def connect(cls, input_node: int, output_node: int) -> bool:
        """Connect an input node to an output or power node."""
        cls.node_relations[input_node] = output_node
        cls.update_simulation()
        return True

    @classmethod
    def disconnect(cls, input_node: int) -> bool:
        """Disconnect an input node."""
        if input_node in cls.node_relations:
            del cls.node_relations[input_node]
            cls.update_simulation()
            return True
        return False

    @classmethod
    def is_input_connected(cls, input_node: int) -> bool:
        """Check if an input node is connected to an output node."""
        return input_node in cls.node_relations

    @classmethod
    def get_connected_output(cls, input_node: int) -> int | None:
        """Get the output node driving this input node, if any."""
        return cls.node_relations.get(input_node)

    @classmethod
    def get_connected_inputs(cls, output_node: int) -> list[int]:
        """Get all input nodes connected to this output node."""
        return [inp for inp, out in cls.node_relations.items() if out == output_node]

    @classmethod
    def set_input_value(cls, input_node: int, value: int) -> bool:
        """
        Set initial input value for an unconnected input node (or toggle power node).
        Connected inputs cannot be manually changed.
        """
        if cls.is_input_connected(input_node):
            return False

        normalized_value = 1 if value else 0
        cls.node_values[input_node] = normalized_value

        if input_node in cls.node_to_ic:
            ic, pin_type, idx = cls.node_to_ic[input_node]
            if pin_type == "input" and idx < len(ic.inputs):
                ic.inputs[idx] = normalized_value
            elif hasattr(ic, "pins") and idx in ic.pins:
                ic.pins[idx].value = normalized_value

        cls.update_simulation()
        return True

    @classmethod
    def toggle_input(cls, input_node: int) -> int | None:
        """
        Toggle an unconnected input or power node between 0 and 1.
        Returns the new value, or None if the input is connected.
        """
        if cls.is_input_connected(input_node):
            return None

        current = cls.node_values.get(input_node, 0)
        new_val = 0 if current == 1 else 1
        cls.set_input_value(input_node, new_val)
        return new_val

    @classmethod
    def update_simulation(cls, max_iterations: int = 32) -> None:
        """
        Propagate signals through all connections and evaluate all ICs
        until steady state or max iterations reached.
        """
        for _ in range(max_iterations):
            changed = False

            # 1. Propagate along wires (connected inputs take driver output's value)
            for inp, out in cls.node_relations.items():
                out_val = cls.node_values.get(out, 0)
                if cls.node_values.get(inp) != out_val:
                    cls.node_values[inp] = out_val
                    changed = True

            # 2. Evaluate ICs
            for ic in cls.ics:
                # Sync IC inputs from node_values
                for i, node_id in enumerate(ic.input_nodes):
                    val = cls.node_values.get(node_id, 0)
                    if i < len(ic.inputs) and ic.inputs[i] != val:
                        ic.inputs[i] = val
                        changed = True

                # If IC has physical pins, sync pin values
                if hasattr(ic, "input_pins"):
                    for pin in ic.input_pins:
                        val = cls.node_values.get(pin.node_id, 0)
                        if pin.value != val:
                            pin.value = val
                            changed = True

                # Run IC logic evaluation
                ic.evaluate()

                # Sync IC outputs to node_values
                for j, node_id in enumerate(ic.output_nodes):
                    if j < len(ic.outputs):
                        val = ic.outputs[j]
                        if cls.node_values.get(node_id) != val:
                            cls.node_values[node_id] = val
                            changed = True

                if hasattr(ic, "output_pins"):
                    for pin in ic.output_pins:
                        val = pin.value
                        if cls.node_values.get(pin.node_id) != val:
                            cls.node_values[pin.node_id] = val
                            changed = True

            if not changed:
                break

    def set_node_relations(
        self, other1: "IC", other2: "IC", node_index_output: int, node_index_input: int
    ) -> None:
        """Backwards-compatible connection helper."""
        out_node = other2.output_nodes[node_index_output]
        in_node = other1.input_nodes[node_index_input]
        self.connect(in_node, out_node)

    def create_ic(self, ic: str) -> None:
        pass
