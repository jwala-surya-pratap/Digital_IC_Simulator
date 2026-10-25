from abc import ABC, abstractmethod

import pygame

class UiDetails:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class UiElement(ABC):
    @abstractmethod
    def event(self, event: pygame.Event) -> None:
        raise Exception("Ui Element event function not implemented")

    @abstractmethod
    def update(self) -> None:
        raise Exception("Ui Element update function not implemented")

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        raise Exception("Ui Element rendre function not implemented")

class UiManager:
    def __init__(self):
        self.name_to_index: dict[str, int] = {}
        self.index_to_details: dict[int, UiDetails] = {}
        self.ui_elements: list[UiElement] = []

    def add(self, name: str, elem: UiElement):
        i = len(self.ui_elements)
        self.name_to_index[name] = i
        self.ui_elements.append(elem)

    def event(self, event: pygame.Event):
        for elem in self.ui_elements:
            elem.event(event)

    def update(self):
        for elem in self.ui_elements:
            elem.update()

    def render(self, surface: pygame.Surface):
        for elem in self.ui_elements:
            elem.render(surface)

    def get_elem(self, name: str) -> UiElement | None:
        if name not in self.name_to_index.keys():
            return None

        return self.ui_elements[self.name_to_index[name]]
