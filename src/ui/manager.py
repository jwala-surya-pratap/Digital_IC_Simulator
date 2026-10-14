import pygame

from .ui_element import UiElement


class Ui:
    count = 0

    def __init__(self) -> None:
        self.id_components: dict[int, UiElement] = {}
        self.name_id: dict[str, int] = {}

    def add_element(self, name: str, element: UiElement) -> None:
        self.count += 1
        id = self.count

        self.id_components.update({id: element})
        self.name_id.update({name: id})

    def remove_element(self, name: str) -> None:
        component_id = self.name_id.pop(name, None)
        if component_id is not None:
            self.id_components.pop(component_id, None)

    def has_element(self, name: str) -> bool:
        return name in self.name_id

    def clear(self) -> None:
        self.id_components.clear()
        self.name_id.clear()

    def get_element(self, name: str) -> UiElement | None:
        if self.name_id.get(name) is None:
            raise ValueError(f"No Ui element found with name: {name}")

        id = self.name_id.get(name) or 0
        return self.id_components.get(id)

    def event(self, event: pygame.event.Event):
        for ui in list(self.id_components.values()):
            ui.event(event)

    def update(self):
        for ui in list(self.id_components.values()):
            ui.update()

    def render(self, surface: pygame.Surface):
        for ui in self.id_components.values():
            ui.render(surface)

