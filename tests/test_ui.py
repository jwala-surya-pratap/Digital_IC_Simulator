import os
import unittest
import pygame

# Use headless video driver for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

from core.ICs import IC, IC7404, IC7408, IC7432
from core.manager import Manager
from ui.elements.button import Button
from ui.elements.canvas import CircuitCanvas
from ui.elements.menu import AddICMenu


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.display = pygame.display.set_mode((1280, 720))
        cls.font = pygame.font.SysFont("monospace", 14)
        cls.small_font = pygame.font.SysFont("monospace", 11)

    def setUp(self):
        Manager.reset()
        self.canvas = CircuitCanvas(
            width=1280,
            height=720,
            font=self.font,
            small_font=self.small_font,
        )

    def test_add_and_remove_ic(self):
        elem = self.canvas.add_ic(IC7408, (100, 100))
        self.assertEqual(len(self.canvas.ic_elements), 1)
        self.assertEqual(elem.ic.name, "7408")

        # Verify real-life pin count and positioning
        self.assertEqual(elem.ic.total_pins, 14)
        self.assertEqual(len(elem.ic.pins), 14)

        # Test remove IC
        self.canvas.remove_ic(elem)
        self.assertEqual(len(self.canvas.ic_elements), 0)
        self.assertEqual(len(Manager.ics), 0)

    def test_visual_wiring_and_manager_sync(self):
        not_elem = self.canvas.add_ic(IC7404, (100, 100))
        and_elem = self.canvas.add_ic(IC7408, (400, 100))

        # Gate 1 NOT output: Pin 2 (1Y)
        out_node = not_elem.ic.output_nodes[0]
        # Gate 1 AND input: Pin 1 (1A)
        in_node = and_elem.ic.input_nodes[0]

        # Connect through canvas
        success = self.canvas.connect_pins(out_node, in_node)
        self.assertTrue(success)
        self.assertEqual(len(self.canvas.wires), 1)
        self.assertEqual(self.canvas.wires[0].output_node, out_node)
        self.assertEqual(self.canvas.wires[0].input_node, in_node)

        # Manager must know the connection
        self.assertTrue(Manager.is_input_connected(in_node))
        self.assertEqual(Manager.get_connected_output(in_node), out_node)

        # Simulation must propagate: NOT output is 1, so AND input 0 is 1
        self.assertEqual(and_elem.ic.inputs[0], 1)

        # Disconnect pin
        self.canvas.disconnect_pin(in_node)
        self.assertEqual(len(self.canvas.wires), 0)
        self.assertFalse(Manager.is_input_connected(in_node))

    def test_input_toggle_via_pin_click(self):
        not_elem = self.canvas.add_ic(IC7404, (100, 100))
        inp_pos = not_elem.get_input_pin_pos(0)
        inp_node = not_elem.ic.input_nodes[0]

        # Initial value is 0
        self.assertEqual(Manager.node_values[inp_node], 0)

        # Simulate left-click on input pin
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": inp_pos}
        )
        self.canvas.event(click_event)

        # Should be toggled to 1
        self.assertEqual(Manager.node_values[inp_node], 1)
        self.assertEqual(not_elem.ic.inputs[0], 1)
        self.assertEqual(not_elem.ic.outputs[0], 0)

    def test_add_ic_menu_dynamic_selection(self):
        selected = []

        def on_select(ic_cls):
            selected.append(ic_cls)

        menu = AddICMenu(
            screen_width=1280,
            screen_height=720,
            font=self.font,
            small_font=self.small_font,
            on_select=on_select,
            on_close=lambda: None,
        )

        # Verify dynamic registration: all classes present
        registered_classes = IC.get_registered_classes()
        self.assertGreaterEqual(len(menu.ic_classes), 3)
        self.assertIn(IC7404, menu.ic_classes)
        self.assertIn(IC7408, menu.ic_classes)
        self.assertIn(IC7432, menu.ic_classes)

        # Click on first card
        first_card_rect = menu.get_card_rect(0)
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": first_card_rect.center}
        )
        menu.event(click_event)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0], menu.ic_classes[0])

    def test_canvas_rendering_does_not_crash(self):
        self.canvas.add_ic(IC7404, (100, 100))
        self.canvas.add_ic(IC7408, (400, 100))
        self.canvas.connect_pins(
            self.canvas.ic_elements[0].ic.output_nodes[0],
            self.canvas.ic_elements[1].ic.input_nodes[0],
        )

        # Render canvas to display surface
        self.canvas.render(self.display)


if __name__ == "__main__":
    unittest.main()
