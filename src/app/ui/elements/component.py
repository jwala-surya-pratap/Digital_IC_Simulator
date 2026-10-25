from typing import Tuple

import pygame

from app.ui.manager import UiElement
from core.component import Component


class ComponentUI(UiElement):
    BG_COLOR = (40, 40, 40)
    INPUT_NODE_COLOR = (100, 100, 100)
    OUTPUT_NODE_COLOR = (150, 150, 150)
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, x: int, y: int, id: int, component: Component, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
        self.id = id
        self.component = component
        self.font = font
        self.small_font = small_font

        max_node_count = max(self.component.input_nodes_count, self.component.output_nodes_count)
        self.bg_rect = pygame.Rect(
            x, y, 65, max_node_count * 50
        )

        self.input_nodes_position: dict[int, Tuple[int, int, int]] = {}
        self.output_nodes_position: dict[int, Tuple[int, int, int]] = {}

        for i, id in enumerate(self.component.input_nodes):
            self.input_nodes_position[id] = (0, 25 * (1 + 2 * i), 10)
        for i, id in enumerate(self.component.output_nodes):
            self.output_nodes_position[id] = (self.bg_rect.width, 25 * (1 + 2 * i), 10)

    def event(self, event: pygame.Event) -> None:
        pass

    def update(self) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.BG_COLOR, self.bg_rect)

        component_name = self.font.render(self.component.name.upper(), True, self.TEXT_COLOR, wraplength=50)
        component_name_rect = component_name.get_rect()
        component_name_rect.center = self.bg_rect.center
        surface.blit(component_name, component_name_rect)

        for stuff in self.input_nodes_position.values():
            pygame.draw.circle(surface, self.INPUT_NODE_COLOR, (self.bg_rect.x + stuff[0], self.bg_rect.y + stuff[1]), stuff[2])
        for stuff in self.output_nodes_position.values():
            pygame.draw.circle(surface, self.OUTPUT_NODE_COLOR, (self.bg_rect.x + stuff[0], self.bg_rect.y + stuff[1]), stuff[2])
