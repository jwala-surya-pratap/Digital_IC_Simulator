from re import T
from typing import Tuple

import pygame
from sys import exit
from app.ui.elements.button import Button, is_button
from app.ui.elements.component import ComponentUI
from app.ui.manager import UiManager
from core.components.and_component import TwoInputAndComponent
from core.components.not_component import OneInputNotComponent
from core.components.or_component import TwoInputOrComponent
from core.manager import ComponentManager

class App:
    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        self.normal_font = pygame.font.SysFont("monospace", 16)
        self.bold_font = pygame.font.SysFont("monospace", 16, bold=True)
        self.italic_font = pygame.font.SysFont("monospace", 16, italic=True)

        # Mouse stuff
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.single_click: bool = False
        self.single_click_count: int = 0
        self.single_click_duration: int = 10
        self.double_click: bool = False

        self.dragged_component: int | None = None
        self.locked_node: int | None = None
        self.locked_node_pos: Tuple[int, int] = (0, 0)

        self.manager = ComponentManager()
        self.ui_components: dict[int, ComponentUI] = {}

        self.ui = UiManager()
        self.ui.add("add_and_btn", Button(20, 20, 80, 30, "2I AND", self.bold_font))
        self.ui.add("add_or_btn", Button(120, 20, 80, 30, "2I OR", self.bold_font))
        self.ui.add("add_not_btn", Button(220, 20, 80, 30, "1I NOT", self.bold_font))
        self.ui.add("add_term_btn", Button(320, 20, 100, 30, "TERMINAL", self.bold_font))

    def event(self, event: pygame.Event):
        # Handle mouse single click and double click
        self.double_click = False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drag_mouse_x = mouse_x - self.prev_mouse_x
        drag_mouse_y = mouse_y - self.prev_mouse_y

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.single_click:
                self.single_click = True
            else:
                self.single_click = False
                self.double_click = True

        self.prev_mouse_x = mouse_x
        self.prev_mouse_y = mouse_y
        if self.single_click:
            self.single_click_count += 1
            if self.single_click_count >= self.single_click_duration:
                self.single_click_count = 0

        # Handle UI stuff
        self.ui.event(event)

        # Handle drawing nodes relations
        if self.locked_node == None:
            for ui in self.ui_components.values():
                for id in ui.input_nodes_position:
                    node_pos = ui.input_nodes_position[id]
                    rect = pygame.Rect(
                        ui.bg_rect.x + node_pos[0] - int(node_pos[2] / 2),
                        ui.bg_rect.y + node_pos[1] - int(node_pos[2] / 2),
                        node_pos[2],
                        node_pos[2]
                    )
                    if self.double_click and rect.collidepoint(mouse_x, mouse_y):
                        self.locked_node = id
                        self.locked_node_pos = rect.center

                for id in ui.output_nodes_position:
                    node_pos = ui.output_nodes_position[id]
                    rect = pygame.Rect(
                        ui.bg_rect.x + node_pos[0] - int(node_pos[2] / 2),
                        ui.bg_rect.y + node_pos[1] - int(node_pos[2] / 2),
                        node_pos[2],
                        node_pos[2]
                    )
                    if self.double_click and rect.collidepoint(mouse_x, mouse_y):
                        self.locked_node = id
                        self.locked_node_pos = rect.center

            # Handle dragging of components
            if self.dragged_component != None:
                self.ui_components[self.dragged_component].bg_rect.x += drag_mouse_x
                self.ui_components[self.dragged_component].bg_rect.y += drag_mouse_y

                if self.double_click:
                    self.dragged_component = None
            else:
                for comp in self.ui_components.values():
                    if self.double_click and comp.bg_rect.collidepoint(mouse_x, mouse_y):
                        self.dragged_component = comp.id
        else:
            for ui in self.ui_components.values():
                for id in ui.input_nodes_position:
                    if id == self.locked_node:
                        break

                    node_pos = ui.input_nodes_position[id]
                    rect = pygame.Rect(
                        ui.bg_rect.x + node_pos[0] - int(node_pos[2] / 2),
                        ui.bg_rect.y + node_pos[1] - int(node_pos[2] / 2),
                        node_pos[2],
                        node_pos[2]
                    )
                    if self.double_click and rect.collidepoint(mouse_x, mouse_y):
                        assert self.locked_node != None
                        self.manager.relate_nodes(self.locked_node, id)
                        self.locked_node = None

                for id in ui.output_nodes_position:
                    if id == self.locked_node:
                        break

                    node_pos = ui.output_nodes_position[id]
                    rect = pygame.Rect(
                        ui.bg_rect.x + node_pos[0] - int(node_pos[2] / 2),
                        ui.bg_rect.y + node_pos[1] - int(node_pos[2] / 2),
                        node_pos[2],
                        node_pos[2]
                    )
                    if self.double_click and rect.collidepoint(mouse_x, mouse_y):
                        assert self.locked_node != None
                        self.manager.relate_nodes(self.locked_node, id)
                        self.locked_node = None


        # COMPONENT ADDING
        and_btn = self.ui.get_elem("add_and_btn")
        if is_button(and_btn):
            if and_btn.is_pressed():
                comp = TwoInputAndComponent()
                id = self.manager.add_component(comp)
                self.ui_components[id] = ComponentUI(100, 100, id, comp, self.normal_font, self.normal_font)

        or_btn = self.ui.get_elem("add_or_btn")
        if is_button(or_btn):
            if or_btn.is_pressed():
                comp = TwoInputOrComponent()
                id = self.manager.add_component(comp)
                self.ui_components[id] = ComponentUI(300, 300, id, comp, self.normal_font, self.normal_font)

        not_btn = self.ui.get_elem("add_not_btn")
        if is_button(not_btn):
            if not_btn.is_pressed():
                comp = OneInputNotComponent()
                id = self.manager.add_component(comp)
                self.ui_components[id] = ComponentUI(300, 300, id, comp, self.normal_font, self.normal_font)

        term_btn = self.ui.get_elem("add_term_btn")
        if is_button(term_btn):
            if term_btn.is_pressed():
                term = TerminalComponent(self.manager, 100, 500, self.normal_font)
                self.terminals.append(term)

    def update(self):
        self.ui.update()

    def render(self):
        # Render Components
        for comp in self.ui_components.values():
            comp.render(self.surface)

        # Render Locking Curve
        if self.locked_node != None:
            pygame.draw.line(self.surface, (0, 255, 0), self.locked_node_pos, pygame.mouse.get_pos(), 3)

        # Render All connected curves
        for start_id in self.manager.node_relations.keys():
            for end_id in self.manager.node_relations[start_id]:
                start_node_pos: Tuple[int, int] | None = None
                end_node_pos: Tuple[int, int] | None = None

                for ui in self.ui_components.values():
                    for id in ui.input_nodes_position:
                        if id == start_id:
                            node_pos = ui.input_nodes_position[id]
                            start_node_pos = (
                                ui.bg_rect.x + node_pos[0],
                                ui.bg_rect.y + node_pos[1]
                            )
                        elif id == end_id:
                            node_pos = ui.input_nodes_position[id]
                            end_node_pos = (
                                ui.bg_rect.x + node_pos[0],
                                ui.bg_rect.y + node_pos[1]
                            )

                    for id in ui.output_nodes_position:
                        if id == start_id:
                            node_pos = ui.output_nodes_position[id]
                            start_node_pos = (
                                ui.bg_rect.x + node_pos[0],
                                ui.bg_rect.y + node_pos[1]
                            )
                        elif id == end_id:
                            node_pos = ui.output_nodes_position[id]
                            end_node_pos = (
                                ui.bg_rect.x + node_pos[0],
                                ui.bg_rect.y + node_pos[1]
                            )

                assert start_node_pos != None
                assert end_node_pos != None
                pygame.draw.line(self.surface, (0, 150, 0), start_node_pos, end_node_pos, width=3)

        self.ui.render(self.surface)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                self.event(event)

            self.surface.fill((0, 0, 0))
            self.update()
            self.render()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    app = App()
    app.run()
