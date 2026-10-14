import os
import unittest
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"

from app.main import App
from core.ICs import IC7432
from core.manager import Manager


class TestSimulatorIntegration(unittest.TestCase):
    def setUp(self):
        Manager.reset()
        self.app = App()

    def test_end_to_end_workflow(self):
        # 1. Verify initial state: default circuit has 7404 and 7408
        self.assertEqual(len(self.app.canvas.ic_elements), 2)
        ic_not = self.app.canvas.ic_elements[0].ic
        ic_and = self.app.canvas.ic_elements[1].ic

        # 7404: 6 inputs, 6 outputs, total 14 pins DIP
        self.assertEqual(ic_not.no_of_inputs, 6)
        self.assertEqual(ic_not.no_of_outputs, 6)
        self.assertEqual(ic_not.inputs[0], 0)
        self.assertEqual(ic_not.outputs[0], 1)

        # 7408: 8 inputs (4 AND gates), 4 outputs, total 14 pins DIP
        self.assertEqual(ic_and.no_of_inputs, 8)
        self.assertEqual(ic_and.no_of_outputs, 4)
        self.assertEqual(ic_and.inputs, [0] * 8)
        self.assertEqual(ic_and.outputs[0], 0)

        # 2. Wire 7404 Gate 1 OUT (Pin 2, 1Y) -> 7408 Gate 1 IN0 (Pin 1, 1A)
        out_node = ic_not.output_nodes[0]
        in0_node = ic_and.input_nodes[0]
        self.app.canvas.connect_pins(out_node, in0_node)

        # Manager must know the connection
        self.assertTrue(Manager.is_input_connected(in0_node))
        self.assertEqual(Manager.get_connected_output(in0_node), out_node)

        # 7408 IN0 is now driven by 7404 OUT (= 1)
        self.assertEqual(ic_and.inputs[0], 1)
        self.assertEqual(ic_and.outputs[0], 0)  # IN1 (Pin 2, 1B) is still 0

        # 3. Toggle unconnected 7408 IN1 (Pin 2, 1B) to 1
        in1_node = ic_and.input_nodes[1]
        self.assertFalse(Manager.is_input_connected(in1_node))
        new_val = Manager.toggle_input(in1_node)
        self.assertEqual(new_val, 1)

        # Both inputs to AND gate 1 are 1, so output 1Y must become 1
        self.assertEqual(ic_and.inputs[:2], [1, 1])
        self.assertEqual(ic_and.outputs[0], 1)

        # 4. Attempt to toggle 7408 IN0: should be disallowed because it's connected
        res = Manager.toggle_input(in0_node)
        self.assertIsNone(res)
        self.assertEqual(ic_and.inputs[0], 1)

        # 5. Toggle 7404 IN (Pin 1, 1A) to 1:
        # 7404 IN = 1 -> 7404 OUT = 0 -> 7408 IN0 = 0 -> 7408 OUT = 0
        not_in_node = ic_not.input_nodes[0]
        Manager.toggle_input(not_in_node)
        self.assertEqual(ic_not.inputs[0], 1)
        self.assertEqual(ic_not.outputs[0], 0)
        self.assertEqual(ic_and.inputs[0], 0)
        self.assertEqual(ic_and.outputs[0], 0)

        # 6. Open Add Menu and dynamically add a 7432 OR gate
        self.app.open_add_menu()
        self.assertIsNotNone(self.app.add_menu)
        self.app.on_select_ic_from_menu(IC7432)
        self.assertIsNone(self.app.add_menu)
        self.assertEqual(len(self.app.canvas.ic_elements), 3)

        # 7. Render a frame to verify no visual or drawing errors
        self.app.update()
        self.app.render()


if __name__ == "__main__":
    unittest.main()
