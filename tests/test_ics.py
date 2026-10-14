import unittest

from core.ICs import (
    IC,
    IC7400,
    IC7402,
    IC7404,
    IC7408,
    IC7432,
    IC7486,
    PinDefinition,
    TestIC,
)
from core.manager import Manager


class TestICs(unittest.TestCase):
    def setUp(self):
        Manager.reset()

    def test_7404_real_life_spec(self):
        ic = IC7404()
        # Real-life DIP-14 specifications
        self.assertEqual(ic.total_pins, 14)
        self.assertEqual(ic.no_of_inputs, 6)
        self.assertEqual(ic.no_of_outputs, 6)
        self.assertEqual(len(ic.pins), 14)
        self.assertEqual(ic.name, "7404")

        # Test Gate 1: Pin 1 (1A) -> Pin 2 (1Y)
        self.assertEqual(ic.get_pin_value(1), 0)
        self.assertEqual(ic.get_pin_value(2), 1)
        Manager.set_input_value(ic.get_pin(1).node_id, 1)
        self.assertEqual(ic.get_pin_value(2), 0)

        # Test Gate 2: Pin 3 (2A) -> Pin 4 (2Y)
        Manager.set_input_value(ic.get_pin(3).node_id, 1)
        self.assertEqual(ic.get_pin_value(4), 0)
        Manager.set_input_value(ic.get_pin(3).node_id, 0)
        self.assertEqual(ic.get_pin_value(4), 1)

        # Test Gate 3: Pin 5 (3A) -> Pin 6 (3Y)
        Manager.set_input_value(ic.get_pin(5).node_id, 1)
        self.assertEqual(ic.get_pin_value(6), 0)

        # Test Gate 4: Pin 9 (4A) -> Pin 8 (4Y)
        Manager.set_input_value(ic.get_pin(9).node_id, 1)
        self.assertEqual(ic.get_pin_value(8), 0)
        Manager.set_input_value(ic.get_pin(9).node_id, 0)
        self.assertEqual(ic.get_pin_value(8), 1)

        # Test Gate 5: Pin 11 (5A) -> Pin 10 (5Y)
        Manager.set_input_value(ic.get_pin(11).node_id, 1)
        self.assertEqual(ic.get_pin_value(10), 0)

        # Test Gate 6: Pin 13 (6A) -> Pin 12 (6Y)
        Manager.set_input_value(ic.get_pin(13).node_id, 1)
        self.assertEqual(ic.get_pin_value(12), 0)

        # Power pin check: Pin 14 is VCC (1), Pin 7 is GND (0)
        self.assertEqual(ic.get_pin_value(14), 1)
        self.assertEqual(ic.get_pin_value(7), 0)
        self.assertTrue(ic.is_powered())

        # If VCC power is lost (0), outputs become 0
        Manager.set_input_value(ic.get_pin(14).node_id, 0)
        self.assertFalse(ic.is_powered())
        self.assertEqual(ic.get_pin_value(2), 0)

    def test_7408_real_life_spec(self):
        ic = IC7408()
        # Real-life DIP-14 specifications
        self.assertEqual(ic.total_pins, 14)
        self.assertEqual(ic.no_of_inputs, 8)
        self.assertEqual(ic.no_of_outputs, 4)
        self.assertEqual(len(ic.pins), 14)
        self.assertEqual(ic.name, "7408")

        # Test Gate 1: Pins 1 (1A), 2 (1B) -> Pin 3 (1Y)
        self.assertEqual(ic.get_pin_value(3), 0)
        Manager.set_input_value(ic.get_pin(1).node_id, 1)
        self.assertEqual(ic.get_pin_value(3), 0)
        Manager.set_input_value(ic.get_pin(2).node_id, 1)
        self.assertEqual(ic.get_pin_value(3), 1)
        Manager.set_input_value(ic.get_pin(1).node_id, 0)
        self.assertEqual(ic.get_pin_value(3), 0)

        # Test Gate 2: Pins 4 (2A), 5 (2B) -> Pin 6 (2Y)
        Manager.set_input_value(ic.get_pin(4).node_id, 1)
        Manager.set_input_value(ic.get_pin(5).node_id, 1)
        self.assertEqual(ic.get_pin_value(6), 1)

        # Test Gate 3: Pins 9 (3A), 10 (3B) -> Pin 8 (3Y)
        Manager.set_input_value(ic.get_pin(9).node_id, 1)
        Manager.set_input_value(ic.get_pin(10).node_id, 1)
        self.assertEqual(ic.get_pin_value(8), 1)

        # Test Gate 4: Pins 12 (4A), 13 (4B) -> Pin 11 (4Y)
        Manager.set_input_value(ic.get_pin(12).node_id, 1)
        Manager.set_input_value(ic.get_pin(13).node_id, 1)
        self.assertEqual(ic.get_pin_value(11), 1)

    def test_7432_real_life_spec(self):
        ic = IC7432()
        # Real-life DIP-14 specifications
        self.assertEqual(ic.total_pins, 14)
        self.assertEqual(ic.no_of_inputs, 8)
        self.assertEqual(ic.no_of_outputs, 4)
        self.assertEqual(len(ic.pins), 14)
        self.assertEqual(ic.name, "7432")

        # Test Gate 1: Pins 1 (1A), 2 (1B) -> Pin 3 (1Y)
        self.assertEqual(ic.get_pin_value(3), 0)
        Manager.set_input_value(ic.get_pin(1).node_id, 1)
        self.assertEqual(ic.get_pin_value(3), 1)
        Manager.set_input_value(ic.get_pin(2).node_id, 1)
        self.assertEqual(ic.get_pin_value(3), 1)
        Manager.set_input_value(ic.get_pin(1).node_id, 0)
        self.assertEqual(ic.get_pin_value(3), 1)
        Manager.set_input_value(ic.get_pin(2).node_id, 0)
        self.assertEqual(ic.get_pin_value(3), 0)

        # Test Gate 2: Pins 4, 5 -> Pin 6
        Manager.set_input_value(ic.get_pin(4).node_id, 1)
        self.assertEqual(ic.get_pin_value(6), 1)

        # Test Gate 3: Pins 9, 10 -> Pin 8
        Manager.set_input_value(ic.get_pin(9).node_id, 1)
        self.assertEqual(ic.get_pin_value(8), 1)

        # Test Gate 4: Pins 12, 13 -> Pin 11
        Manager.set_input_value(ic.get_pin(12).node_id, 1)
        self.assertEqual(ic.get_pin_value(11), 1)

    def test_future_proof_subclass_registration(self):
        """Verify that any new IC subclass automatically registers in the catalog."""

        class IC7410(IC):
            chip_name = "7410"
            type_name = "Triple 3-Input NAND"
            description = "3 NAND Gates (3 inputs each) • 14-pin DIP"
            total_pins = 14
            pin_definitions = [
                PinDefinition(1, "1A", "input", gate_index=0),
                PinDefinition(2, "1B", "input", gate_index=0),
                PinDefinition(3, "2A", "input", gate_index=1),
                PinDefinition(4, "2B", "input", gate_index=1),
                PinDefinition(5, "2C", "input", gate_index=1),
                PinDefinition(6, "2Y", "output", gate_index=1),
                PinDefinition(7, "GND", "gnd"),
                PinDefinition(8, "3Y", "output", gate_index=2),
                PinDefinition(9, "3A", "input", gate_index=2),
                PinDefinition(10, "3B", "input", gate_index=2),
                PinDefinition(11, "3C", "input", gate_index=2),
                PinDefinition(12, "1Y", "output", gate_index=0),
                PinDefinition(13, "1C", "input", gate_index=0),
                PinDefinition(14, "VCC", "vcc"),
            ]

            def evaluate(self) -> None:
                if not self.is_powered():
                    self.clear_outputs()
                    return
                # Gate 1: 1Y = NOT (1A and 1B and 1C)
                nand1 = not (
                    self.get_pin_value(1) == 1
                    and self.get_pin_value(2) == 1
                    and self.get_pin_value(13) == 1
                )
                self.set_pin_value(12, 1 if nand1 else 0)

        # Automatically in catalog!
        registered = IC.get_registered_classes()
        self.assertIn(IC7410, registered)
        self.assertEqual(IC.get_registered_class("7410"), IC7410)

        # Instance test
        custom_ic = IC7410()
        self.assertEqual(custom_ic.get_pin_value(12), 1)  # Initial 0,0,0 -> 1
        Manager.set_input_value(custom_ic.get_pin(1).node_id, 1)
        Manager.set_input_value(custom_ic.get_pin(2).node_id, 1)
        Manager.set_input_value(custom_ic.get_pin(13).node_id, 1)
        self.assertEqual(custom_ic.get_pin_value(12), 0)  # 1,1,1 -> 0

    def test_7400_nand_gate(self):
        ic = IC7400()
        self.assertEqual(ic.outputs[0], 1)
        Manager.set_input_value(ic.input_nodes[0], 1)
        self.assertEqual(ic.outputs[0], 1)
        Manager.set_input_value(ic.input_nodes[1], 1)
        self.assertEqual(ic.outputs[0], 0)

    def test_7402_nor_gate(self):
        ic = IC7402()
        self.assertEqual(ic.outputs[0], 1)
        Manager.set_input_value(ic.input_nodes[0], 1)
        self.assertEqual(ic.outputs[0], 0)
        Manager.set_input_value(ic.input_nodes[1], 1)
        self.assertEqual(ic.outputs[0], 0)

    def test_7486_xor_gate(self):
        ic = IC7486()
        self.assertEqual(ic.outputs[0], 0)
        Manager.set_input_value(ic.input_nodes[0], 1)
        self.assertEqual(ic.outputs[0], 1)
        Manager.set_input_value(ic.input_nodes[1], 1)
        self.assertEqual(ic.outputs[0], 0)
        Manager.set_input_value(ic.input_nodes[0], 0)
        self.assertEqual(ic.outputs[0], 1)

    def test_test_ic_buffer(self):
        ic = TestIC()
        self.assertEqual(ic.outputs[0], 0)
        Manager.set_input_value(ic.input_nodes[0], 1)
        self.assertEqual(ic.outputs[0], 1)


if __name__ == "__main__":
    unittest.main()
