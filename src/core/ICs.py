from __future__ import annotations

import sys
from typing import Type

from .manager import Manager

no_of_ics: int = 0


class PinDefinition:
    """Specification of a physical pin on an IC."""

    def __init__(
        self,
        number: int,
        name: str,
        pin_type: str,  # "input", "output", "vcc", "gnd", "nc"
        description: str = "",
        gate_index: int | None = None,
        default_value: int = 0,
    ) -> None:
        self.number = number
        self.name = name
        self.pin_type = pin_type.lower()
        self.description = description
        self.gate_index = gate_index
        self.default_value = default_value


class Pin:
    """An active pin on an instantiated IC linked to a simulation node."""

    def __init__(
        self,
        number: int,
        name: str,
        pin_type: str,
        description: str = "",
        gate_index: int | None = None,
        node_id: int = 0,
        initial_value: int = 0,
    ) -> None:
        self.number = number
        self.name = name
        self.pin_type = pin_type.lower()
        self.description = description
        self.gate_index = gate_index
        self.node_id = node_id
        self.value = initial_value

    @property
    def is_input(self) -> bool:
        return self.pin_type == "input"

    @property
    def is_output(self) -> bool:
        return self.pin_type == "output"

    @property
    def is_vcc(self) -> bool:
        return self.pin_type == "vcc"

    @property
    def is_gnd(self) -> bool:
        return self.pin_type == "gnd"

    @property
    def is_power(self) -> bool:
        return self.pin_type in ("vcc", "gnd")


class IC:
    """
    Base class for all Integrated Circuit (IC) chips.

    Subclasses define real-life DIP pinouts and logic operations.
    Any new subclass is automatically discovered and registered
    via __init_subclass__, future-proofing the simulator.
    """

    # Class-level registry of available IC classes
    _registry: dict[str, Type["IC"]] = {}

    chip_name: str = "IC"
    type_name: str = "Generic IC"
    description: str = "Generic Integrated Circuit"
    total_pins: int = 14
    pin_definitions: list[PinDefinition] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register concrete IC classes that provide a chip_name and aren't marked as tests
        if (
            hasattr(cls, "chip_name")
            and cls.chip_name != "IC"
            and not getattr(cls, "__test__", False)
        ):
            cls._registry[cls.chip_name] = cls

    @classmethod
    def get_registered_classes(cls) -> list[Type["IC"]]:
        """Return a list of all registered IC classes."""
        return list(cls._registry.values())

    @classmethod
    def get_registered_class(cls, chip_name: str) -> Type["IC"] | None:
        """Lookup an IC class by its chip name (e.g. '7404')."""
        return cls._registry.get(chip_name)

    @classmethod
    def register(cls, ic_cls: Type["IC"]) -> Type["IC"]:
        """Explicitly register an IC class in the catalog."""
        cls._registry[ic_cls.chip_name] = ic_cls
        return ic_cls

    def __init__(
        self,
        no_of_inputs: int | None = None,
        no_of_outputs: int | None = None,
        name: str | None = None,
        type_name: str | None = None,
    ) -> None:
        global no_of_ics
        no_of_ics += 1

        self.name = name if name is not None else self.chip_name
        self.type_name = type_name if type_name is not None else self.__class__.type_name

        self.pins: dict[int, Pin] = {}
        self.input_pins: list[Pin] = []
        self.output_pins: list[Pin] = []
        self.vcc_pin: Pin | None = None
        self.gnd_pin: Pin | None = None

        if self.pin_definitions:
            # Allocate pins based on real-life pin definitions
            for pdef in self.pin_definitions:
                Manager.counter += 1
                node_id = Manager.counter
                default_val = (
                    1 if pdef.pin_type == "vcc" else (0 if pdef.pin_type == "gnd" else pdef.default_value)
                )
                Manager.node_values[node_id] = default_val

                pin = Pin(
                    number=pdef.number,
                    name=pdef.name,
                    pin_type=pdef.pin_type,
                    description=pdef.description,
                    gate_index=pdef.gate_index,
                    node_id=node_id,
                    initial_value=default_val,
                )
                self.pins[pin.number] = pin

                if pin.is_input:
                    self.input_pins.append(pin)
                elif pin.is_output:
                    self.output_pins.append(pin)
                elif pin.is_vcc:
                    self.vcc_pin = pin
                elif pin.is_gnd:
                    self.gnd_pin = pin

            self.input_nodes: list[int] = [p.node_id for p in self.input_pins]
            self.output_nodes: list[int] = [p.node_id for p in self.output_pins]

            self.no_of_inputs = len(self.input_nodes)
            self.no_of_outputs = len(self.output_nodes)
        else:
            # Fallback for generic or legacy ICs with ad-hoc input/output counts
            self.no_of_inputs = no_of_inputs if no_of_inputs is not None else 1
            self.no_of_outputs = no_of_outputs if no_of_outputs is not None else 1

            self.input_nodes, self.output_nodes = Manager.get_nodes(
                self.no_of_inputs, self.no_of_outputs
            )

            # Generate synthetic pin entries
            pin_num = 1
            for i, nid in enumerate(self.input_nodes):
                pin = Pin(pin_num, f"IN{i}", "input", node_id=nid)
                self.pins[pin_num] = pin
                self.input_pins.append(pin)
                pin_num += 1

            for j, nid in enumerate(self.output_nodes):
                pin = Pin(pin_num, f"OUT{j}", "output", node_id=nid)
                self.pins[pin_num] = pin
                self.output_pins.append(pin)
                pin_num += 1

        self.node_start_value = Manager.counter
        self.inputs: list[int] = [p.value for p in self.input_pins]
        self.outputs: list[int] = [p.value for p in self.output_pins]

        Manager.register_ic(self)
        self.evaluate()

    def get_pin(self, number: int) -> Pin | None:
        """Get pin object by physical pin number (1..total_pins)."""
        return self.pins.get(number)

    def get_pin_value(self, number: int) -> int:
        """Get current logic value (0 or 1) of a physical pin."""
        pin = self.pins.get(number)
        if pin is not None:
            return Manager.node_values.get(pin.node_id, pin.value)
        return 0

    def set_pin_value(self, number: int, value: int) -> None:
        """Set output logic value on a physical pin."""
        pin = self.pins.get(number)
        if pin is not None:
            norm = 1 if value else 0
            pin.value = norm
            Manager.node_values[pin.node_id] = norm
            if pin in self.output_pins:
                idx = self.output_pins.index(pin)
                if idx < len(self.outputs):
                    self.outputs[idx] = norm

    def is_powered(self) -> bool:
        """
        Check if IC has power applied according to real-life TTL specifications:
        VCC (Pin 14) must be HIGH (1) and GND (Pin 7) must be LOW (0).
        """
        if self.vcc_pin is not None:
            vcc_val = Manager.node_values.get(self.vcc_pin.node_id, self.vcc_pin.value)
            if vcc_val != 1:
                return False

        if self.gnd_pin is not None:
            gnd_val = Manager.node_values.get(self.gnd_pin.node_id, self.gnd_pin.value)
            if gnd_val != 0:
                return False

        return True

    def clear_outputs(self) -> None:
        """Drive all outputs to LOW (0) when unpowered."""
        for pin in self.output_pins:
            self.set_pin_value(pin.number, 0)

    def evaluate(self) -> None:
        """
        Evaluate IC logic. Subclasses implement the exact gate logic
        mapped to real-life physical pin numbers.
        """
        pass

    def operation(self) -> None:
        """Alias for evaluate."""
        self.evaluate()

    def input_values(self, values: list[int] | None = None) -> None:
        """
        Accept programmatic initial inputs (from UI or caller) or fallback
        to interactive prompt if running in an interactive terminal.
        """
        if values is not None:
            for i, val in enumerate(values[: self.no_of_inputs]):
                Manager.set_input_value(self.input_nodes[i], val)
            return

        if sys.stdin.isatty():
            for i in range(self.no_of_inputs):
                try:
                    entry = int(input(f"Input {i}: "))
                    Manager.set_input_value(self.input_nodes[i], entry)
                except (ValueError, EOFError):
                    break


class IC7404(IC):
    """
    7404: Hex Inverter (NOT Gate).
    Real-life 14-pin DIP package with 6 independent NOT gates.

    Real-life Pinout:
      Pin 1:  1A (Input 1)  --> Pin 2:  1Y (Output 1)
      Pin 3:  2A (Input 2)  --> Pin 4:  2Y (Output 2)
      Pin 5:  3A (Input 3)  --> Pin 6:  3Y (Output 3)
      Pin 7:  GND (0V)
      Pin 9:  4A (Input 4)  --> Pin 8:  4Y (Output 4)
      Pin 11: 5A (Input 5)  --> Pin 10: 5Y (Output 5)
      Pin 13: 6A (Input 6)  --> Pin 12: 6Y (Output 6)
      Pin 14: VCC (+5V)
    """

    chip_name = "7404"
    type_name = "Hex Inverter"
    description = "6 NOT Gates • 14-pin DIP • Real-life pinout (6 In, 6 Out)"
    total_pins = 14

    pin_definitions = [
        PinDefinition(1, "1A", "input", "Gate 1 Input", gate_index=0),
        PinDefinition(2, "1Y", "output", "Gate 1 Output (NOT 1A)", gate_index=0),
        PinDefinition(3, "2A", "input", "Gate 2 Input", gate_index=1),
        PinDefinition(4, "2Y", "output", "Gate 2 Output (NOT 2A)", gate_index=1),
        PinDefinition(5, "3A", "input", "Gate 3 Input", gate_index=2),
        PinDefinition(6, "3Y", "output", "Gate 3 Output (NOT 3A)", gate_index=2),
        PinDefinition(7, "GND", "gnd", "Ground (0V)"),
        PinDefinition(8, "4Y", "output", "Gate 4 Output (NOT 4A)", gate_index=3),
        PinDefinition(9, "4A", "input", "Gate 4 Input", gate_index=3),
        PinDefinition(10, "5Y", "output", "Gate 5 Output (NOT 5A)", gate_index=4),
        PinDefinition(11, "5A", "input", "Gate 5 Input", gate_index=4),
        PinDefinition(12, "6Y", "output", "Gate 6 Output (NOT 6A)", gate_index=5),
        PinDefinition(13, "6A", "input", "Gate 6 Input", gate_index=5),
        PinDefinition(14, "VCC", "vcc", "Supply Voltage (+5V)"),
    ]

    def evaluate(self) -> None:
        if not self.is_powered():
            self.clear_outputs()
            return

        # Gate 1: 1Y = NOT 1A (Pin 1 -> Pin 2)
        self.set_pin_value(2, 0 if self.get_pin_value(1) == 1 else 1)
        # Gate 2: 2Y = NOT 2A (Pin 3 -> Pin 4)
        self.set_pin_value(4, 0 if self.get_pin_value(3) == 1 else 1)
        # Gate 3: 3Y = NOT 3A (Pin 5 -> Pin 6)
        self.set_pin_value(6, 0 if self.get_pin_value(5) == 1 else 1)
        # Gate 4: 4Y = NOT 4A (Pin 9 -> Pin 8)
        self.set_pin_value(8, 0 if self.get_pin_value(9) == 1 else 1)
        # Gate 5: 5Y = NOT 5A (Pin 11 -> Pin 10)
        self.set_pin_value(10, 0 if self.get_pin_value(11) == 1 else 1)
        # Gate 6: 6Y = NOT 6A (Pin 13 -> Pin 12)
        self.set_pin_value(12, 0 if self.get_pin_value(13) == 1 else 1)


class IC7408(IC):
    """
    7408: Quad 2-Input AND Gate.
    Real-life 14-pin DIP package with 4 independent 2-input AND gates.

    Real-life Pinout:
      Pin 1:  1A, Pin 2:  1B  --> Pin 3:  1Y (Output 1 = 1A AND 1B)
      Pin 4:  2A, Pin 5:  2B  --> Pin 6:  2Y (Output 2 = 2A AND 2B)
      Pin 7:  GND (0V)
      Pin 9:  3A, Pin 10: 3B  --> Pin 8:  3Y (Output 3 = 3A AND 3B)
      Pin 12: 4A, Pin 13: 4B  --> Pin 11: 4Y (Output 4 = 4A AND 4B)
      Pin 14: VCC (+5V)
    """

    chip_name = "7408"
    type_name = "Quad 2-Input AND"
    description = "4 AND Gates • 14-pin DIP • Real-life pinout (8 In, 4 Out)"
    total_pins = 14

    pin_definitions = [
        PinDefinition(1, "1A", "input", "Gate 1 Input A", gate_index=0),
        PinDefinition(2, "1B", "input", "Gate 1 Input B", gate_index=0),
        PinDefinition(3, "1Y", "output", "Gate 1 Output (1A AND 1B)", gate_index=0),
        PinDefinition(4, "2A", "input", "Gate 2 Input A", gate_index=1),
        PinDefinition(5, "2B", "input", "Gate 2 Input B", gate_index=1),
        PinDefinition(6, "2Y", "output", "Gate 2 Output (2A AND 2B)", gate_index=1),
        PinDefinition(7, "GND", "gnd", "Ground (0V)"),
        PinDefinition(8, "3Y", "output", "Gate 3 Output (3A AND 3B)", gate_index=2),
        PinDefinition(9, "3A", "input", "Gate 3 Input A", gate_index=2),
        PinDefinition(10, "3B", "input", "Gate 3 Input B", gate_index=2),
        PinDefinition(11, "4Y", "output", "Gate 4 Output (4A AND 4B)", gate_index=3),
        PinDefinition(12, "4A", "input", "Gate 4 Input A", gate_index=3),
        PinDefinition(13, "4B", "input", "Gate 4 Input B", gate_index=3),
        PinDefinition(14, "VCC", "vcc", "Supply Voltage (+5V)"),
    ]

    def evaluate(self) -> None:
        if not self.is_powered():
            self.clear_outputs()
            return

        # Gate 1: 1Y = 1A AND 1B (Pins 1, 2 -> Pin 3)
        self.set_pin_value(
            3, 1 if (self.get_pin_value(1) == 1 and self.get_pin_value(2) == 1) else 0
        )
        # Gate 2: 2Y = 2A AND 2B (Pins 4, 5 -> Pin 6)
        self.set_pin_value(
            6, 1 if (self.get_pin_value(4) == 1 and self.get_pin_value(5) == 1) else 0
        )
        # Gate 3: 3Y = 3A AND 3B (Pins 9, 10 -> Pin 8)
        self.set_pin_value(
            8, 1 if (self.get_pin_value(9) == 1 and self.get_pin_value(10) == 1) else 0
        )
        # Gate 4: 4Y = 4A AND 4B (Pins 12, 13 -> Pin 11)
        self.set_pin_value(
            11, 1 if (self.get_pin_value(12) == 1 and self.get_pin_value(13) == 1) else 0
        )


class IC7432(IC):
    """
    7432: Quad 2-Input OR Gate.
    Real-life 14-pin DIP package with 4 independent 2-input OR gates.

    Real-life Pinout:
      Pin 1:  1A, Pin 2:  1B  --> Pin 3:  1Y (Output 1 = 1A OR 1B)
      Pin 4:  2A, Pin 5:  2B  --> Pin 6:  2Y (Output 2 = 2A OR 2B)
      Pin 7:  GND (0V)
      Pin 9:  3A, Pin 10: 3B  --> Pin 8:  3Y (Output 3 = 3A OR 3B)
      Pin 12: 4A, Pin 13: 4B  --> Pin 11: 4Y (Output 4 = 4A OR 4B)
      Pin 14: VCC (+5V)
    """

    chip_name = "7432"
    type_name = "Quad 2-Input OR"
    description = "4 OR Gates • 14-pin DIP • Real-life pinout (8 In, 4 Out)"
    total_pins = 14

    pin_definitions = [
        PinDefinition(1, "1A", "input", "Gate 1 Input A", gate_index=0),
        PinDefinition(2, "1B", "input", "Gate 1 Input B", gate_index=0),
        PinDefinition(3, "1Y", "output", "Gate 1 Output (1A OR 1B)", gate_index=0),
        PinDefinition(4, "2A", "input", "Gate 2 Input A", gate_index=1),
        PinDefinition(5, "2B", "input", "Gate 2 Input B", gate_index=1),
        PinDefinition(6, "2Y", "output", "Gate 2 Output (2A OR 2B)", gate_index=1),
        PinDefinition(7, "GND", "gnd", "Ground (0V)"),
        PinDefinition(8, "3Y", "output", "Gate 3 Output (3A OR 3B)", gate_index=2),
        PinDefinition(9, "3A", "input", "Gate 3 Input A", gate_index=2),
        PinDefinition(10, "3B", "input", "Gate 3 Input B", gate_index=2),
        PinDefinition(11, "4Y", "output", "Gate 4 Output (4A OR 4B)", gate_index=3),
        PinDefinition(12, "4A", "input", "Gate 4 Input A", gate_index=3),
        PinDefinition(13, "4B", "input", "Gate 4 Input B", gate_index=3),
        PinDefinition(14, "VCC", "vcc", "Supply Voltage (+5V)"),
    ]

    def evaluate(self) -> None:
        if not self.is_powered():
            self.clear_outputs()
            return

        # Gate 1: 1Y = 1A OR 1B (Pins 1, 2 -> Pin 3)
        self.set_pin_value(
            3, 1 if (self.get_pin_value(1) == 1 or self.get_pin_value(2) == 1) else 0
        )
        # Gate 2: 2Y = 2A OR 2B (Pins 4, 5 -> Pin 6)
        self.set_pin_value(
            6, 1 if (self.get_pin_value(4) == 1 or self.get_pin_value(5) == 1) else 0
        )
        # Gate 3: 3Y = 3A OR 3B (Pins 9, 10 -> Pin 8)
        self.set_pin_value(
            8, 1 if (self.get_pin_value(9) == 1 or self.get_pin_value(10) == 1) else 0
        )
        # Gate 4: 4Y = 4A OR 4B (Pins 12, 13 -> Pin 11)
        self.set_pin_value(
            11, 1 if (self.get_pin_value(12) == 1 or self.get_pin_value(13) == 1) else 0
        )


class IC7400(IC):
    """
    7400: Quad 2-Input NAND Gate.
    Real-life 14-pin DIP package with 4 independent 2-input NAND gates.
    """

    chip_name = "7400"
    type_name = "Quad 2-Input NAND"
    description = "4 NAND Gates • 14-pin DIP • Real-life pinout (8 In, 4 Out)"
    total_pins = 14

    pin_definitions = [
        PinDefinition(1, "1A", "input", "Gate 1 Input A", gate_index=0),
        PinDefinition(2, "1B", "input", "Gate 1 Input B", gate_index=0),
        PinDefinition(3, "1Y", "output", "Gate 1 Output (1A NAND 1B)", gate_index=0),
        PinDefinition(4, "2A", "input", "Gate 2 Input A", gate_index=1),
        PinDefinition(5, "2B", "input", "Gate 2 Input B", gate_index=1),
        PinDefinition(6, "2Y", "output", "Gate 2 Output (2A NAND 2B)", gate_index=1),
        PinDefinition(7, "GND", "gnd", "Ground (0V)"),
        PinDefinition(8, "3Y", "output", "Gate 3 Output (3A NAND 3B)", gate_index=2),
        PinDefinition(9, "3A", "input", "Gate 3 Input A", gate_index=2),
        PinDefinition(10, "3B", "input", "Gate 3 Input B", gate_index=2),
        PinDefinition(11, "4Y", "output", "Gate 4 Output (4A NAND 4B)", gate_index=3),
        PinDefinition(12, "4A", "input", "Gate 4 Input A", gate_index=3),
        PinDefinition(13, "4B", "input", "Gate 4 Input B", gate_index=3),
        PinDefinition(14, "VCC", "vcc", "Supply Voltage (+5V)"),
    ]

    def evaluate(self) -> None:
        if not self.is_powered():
            self.clear_outputs()
            return

        self.set_pin_value(
            3, 0 if (self.get_pin_value(1) == 1 and self.get_pin_value(2) == 1) else 1
        )
        self.set_pin_value(
            6, 0 if (self.get_pin_value(4) == 1 and self.get_pin_value(5) == 1) else 1
        )
        self.set_pin_value(
            8, 0 if (self.get_pin_value(9) == 1 and self.get_pin_value(10) == 1) else 1
        )
        self.set_pin_value(
            11, 0 if (self.get_pin_value(12) == 1 and self.get_pin_value(13) == 1) else 1
        )


class IC7402(IC):
    """
    7402: Quad 2-Input NOR Gate.
    Real-life 14-pin DIP package with 4 independent 2-input NOR gates.
    Note real-life 7402 pinout: outputs are Pins 1, 4, 10, 13.
    """

    chip_name = "7402"
    type_name = "Quad 2-Input NOR"
    description = "4 NOR Gates • 14-pin DIP • Real-life pinout (8 In, 4 Out)"
    total_pins = 14

    pin_definitions = [
        PinDefinition(1, "1Y", "output", "Gate 1 Output (1A NOR 1B)", gate_index=0),
        PinDefinition(2, "1A", "input", "Gate 1 Input A", gate_index=0),
        PinDefinition(3, "1B", "input", "Gate 1 Input B", gate_index=0),
        PinDefinition(4, "2Y", "output", "Gate 2 Output (2A NOR 2B)", gate_index=1),
        PinDefinition(5, "2A", "input", "Gate 2 Input A", gate_index=1),
        PinDefinition(6, "2B", "input", "Gate 2 Input B", gate_index=1),
        PinDefinition(7, "GND", "gnd", "Ground (0V)"),
        PinDefinition(8, "3A", "input", "Gate 3 Input A", gate_index=2),
        PinDefinition(9, "3B", "input", "Gate 3 Input B", gate_index=2),
        PinDefinition(10, "3Y", "output", "Gate 3 Output (3A NOR 3B)", gate_index=2),
        PinDefinition(11, "4A", "input", "Gate 4 Input A", gate_index=3),
        PinDefinition(12, "4B", "input", "Gate 4 Input B", gate_index=3),
        PinDefinition(13, "4Y", "output", "Gate 4 Output (4A NOR 4B)", gate_index=3),
        PinDefinition(14, "VCC", "vcc", "Supply Voltage (+5V)"),
    ]

    def evaluate(self) -> None:
        if not self.is_powered():
            self.clear_outputs()
            return

        self.set_pin_value(
            1, 1 if (self.get_pin_value(2) == 0 and self.get_pin_value(3) == 0) else 0
        )
        self.set_pin_value(
            4, 1 if (self.get_pin_value(5) == 0 and self.get_pin_value(6) == 0) else 0
        )
        self.set_pin_value(
            10, 1 if (self.get_pin_value(8) == 0 and self.get_pin_value(9) == 0) else 0
        )
        self.set_pin_value(
            13, 1 if (self.get_pin_value(11) == 0 and self.get_pin_value(12) == 0) else 0
        )


class IC7486(IC):
    """
    7486: Quad 2-Input XOR Gate.
    Real-life 14-pin DIP package with 4 independent 2-input XOR gates.
    """

    chip_name = "7486"
    type_name = "Quad 2-Input XOR"
    description = "4 XOR Gates • 14-pin DIP • Real-life pinout (8 In, 4 Out)"
    total_pins = 14

    pin_definitions = [
        PinDefinition(1, "1A", "input", "Gate 1 Input A", gate_index=0),
        PinDefinition(2, "1B", "input", "Gate 1 Input B", gate_index=0),
        PinDefinition(3, "1Y", "output", "Gate 1 Output (1A XOR 1B)", gate_index=0),
        PinDefinition(4, "2A", "input", "Gate 2 Input A", gate_index=1),
        PinDefinition(5, "2B", "input", "Gate 2 Input B", gate_index=1),
        PinDefinition(6, "2Y", "output", "Gate 2 Output (2A XOR 2B)", gate_index=1),
        PinDefinition(7, "GND", "gnd", "Ground (0V)"),
        PinDefinition(8, "3Y", "output", "Gate 3 Output (3A XOR 3B)", gate_index=2),
        PinDefinition(9, "3A", "input", "Gate 3 Input A", gate_index=2),
        PinDefinition(10, "3B", "input", "Gate 3 Input B", gate_index=2),
        PinDefinition(11, "4Y", "output", "Gate 4 Output (4A XOR 4B)", gate_index=3),
        PinDefinition(12, "4A", "input", "Gate 4 Input A", gate_index=3),
        PinDefinition(13, "4B", "input", "Gate 4 Input B", gate_index=3),
        PinDefinition(14, "VCC", "vcc", "Supply Voltage (+5V)"),
    ]

    def evaluate(self) -> None:
        if not self.is_powered():
            self.clear_outputs()
            return

        self.set_pin_value(
            3, 1 if (self.get_pin_value(1) ^ self.get_pin_value(2)) == 1 else 0
        )
        self.set_pin_value(
            6, 1 if (self.get_pin_value(4) ^ self.get_pin_value(5)) == 1 else 0
        )
        self.set_pin_value(
            8, 1 if (self.get_pin_value(9) ^ self.get_pin_value(10)) == 1 else 0
        )
        self.set_pin_value(
            11, 1 if (self.get_pin_value(12) ^ self.get_pin_value(13)) == 1 else 0
        )


class TestIC(IC):
    """Test IC (Buffer) for backward compatibility in test suites."""

    __test__ = False
    chip_name = "TestIC"
    type_name = "Buffer"

    def __init__(self) -> None:
        super().__init__(no_of_inputs=1, no_of_outputs=1, name="TestIC", type_name="Buffer")

    def evaluate(self) -> None:
        if self.no_of_inputs >= 1 and self.no_of_outputs >= 1:
            self.outputs[0] = self.inputs[0]


# Backwards compatibility dictionary
AVAILABLE_ICS: dict[str, Type[IC]] = IC._registry
