import unittest

from core.ICs import IC7404, IC7408, IC7432
from core.manager import Manager


class TestManager(unittest.TestCase):
    def setUp(self):
        Manager.reset()

    def test_node_allocation(self):
        in_nodes, out_nodes = Manager.get_nodes(2, 1)
        self.assertEqual(len(in_nodes), 2)
        self.assertEqual(len(out_nodes), 1)
        self.assertEqual(Manager.node_values[in_nodes[0]], 0)
        self.assertEqual(Manager.node_values[in_nodes[1]], 0)
        self.assertEqual(Manager.node_values[out_nodes[0]], 0)

    def test_unconnected_input_toggle(self):
        not_gate = IC7404()
        inp = not_gate.input_nodes[0]
        self.assertFalse(Manager.is_input_connected(inp))

        # Initial value is 0, so NOT gate output is 1
        self.assertEqual(Manager.node_values[inp], 0)
        self.assertEqual(not_gate.inputs[0], 0)
        self.assertEqual(not_gate.outputs[0], 1)

        # Toggle input to 1
        new_val = Manager.toggle_input(inp)
        self.assertEqual(new_val, 1)
        self.assertEqual(Manager.node_values[inp], 1)
        self.assertEqual(not_gate.inputs[0], 1)
        self.assertEqual(not_gate.outputs[0], 0)
        self.assertEqual(Manager.node_values[not_gate.output_nodes[0]], 0)

        # Toggle back to 0
        new_val = Manager.toggle_input(inp)
        self.assertEqual(new_val, 0)
        self.assertEqual(not_gate.outputs[0], 1)

    def test_connected_input_cannot_be_toggled(self):
        not_gate = IC7404()
        and_gate = IC7408()

        # Connect NOT output to AND input 0
        Manager.connect(and_gate.input_nodes[0], not_gate.output_nodes[0])
        self.assertTrue(Manager.is_input_connected(and_gate.input_nodes[0]))

        # The input value is driven by NOT output (which is 1 since NOT input is 0)
        self.assertEqual(and_gate.inputs[0], 1)

        # Attempt to manually toggle the connected input: must fail and return None
        res = Manager.toggle_input(and_gate.input_nodes[0])
        self.assertIsNone(res)
        self.assertEqual(and_gate.inputs[0], 1)

        # Also direct set_input_value must return False
        set_res = Manager.set_input_value(and_gate.input_nodes[0], 0)
        self.assertFalse(set_res)
        self.assertEqual(and_gate.inputs[0], 1)

    def test_propagation_across_connected_ics(self):
        not_gate = IC7404()  # IN: 0 -> OUT: 1
        and_gate = IC7408()  # IN0, IN1 -> OUT

        # Connect NOT output to AND input 0
        Manager.connect(and_gate.input_nodes[0], not_gate.output_nodes[0])
        self.assertEqual(and_gate.inputs[0], 1)

        # Toggle unconnected AND input 1 to 1
        Manager.toggle_input(and_gate.input_nodes[1])
        self.assertEqual(and_gate.inputs[1], 1)

        # Both AND inputs are 1, so AND output should be 1
        self.assertEqual(and_gate.outputs[0], 1)

        # Now toggle NOT input to 1:
        # NOT input: 1 -> NOT output: 0 -> AND input 0: 0 -> AND output: 0
        Manager.toggle_input(not_gate.input_nodes[0])
        self.assertEqual(not_gate.outputs[0], 0)
        self.assertEqual(and_gate.inputs[0], 0)
        self.assertEqual(and_gate.outputs[0], 0)

    def test_disconnect(self):
        not_gate = IC7404()
        and_gate = IC7408()

        Manager.connect(and_gate.input_nodes[0], not_gate.output_nodes[0])
        self.assertTrue(Manager.is_input_connected(and_gate.input_nodes[0]))

        # Disconnect
        Manager.disconnect(and_gate.input_nodes[0])
        self.assertFalse(Manager.is_input_connected(and_gate.input_nodes[0]))

        # Now it should be manually toggleable again
        res = Manager.toggle_input(and_gate.input_nodes[0])
        self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()
