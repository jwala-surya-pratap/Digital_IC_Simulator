import pygame

from .ui_element import UiElement

class Ui:
    count = 0

    def __init__(self) -> None:
        self.id_components: dict[int, UiElement] = {}
        self.name_id: dict[str, int] = {}

    def add_element(self, name: str, element: UiElement):
        self.count += 1
        id = self.count

        self.id_components.update({ id: element })
        self.name_id.update({ name: id })

    def get_element(self, name: str) -> UiElement | None:
        if self.name_id.get(name) is None:
            raise ValueError(f"No Ui element found with name: {name}")

        id = self.name_id.get(name) or 0
        return self.id_components.get(id)

    def event(self, event: pygame.event.Event):
        for ui in self.id_components.values():
            ui.event(event)

    def update(self):
        for ui in self.id_components.values():
            ui.update()

    def render(self, surface: pygame.Surface):
        for ui in self.id_components.values():
            ui.render(surface)
