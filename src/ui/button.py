from typing import Tuple
import pygame

ColorTuple = Tuple[int, int, int]

class Button:
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        text: str, 
        font: pygame.font.Font, 
        bg_color: ColorTuple = (50, 50, 50), 
        hover_color: ColorTuple = (80, 80, 80), 
        text_color: ColorTuple = (255, 255, 255), 
        border_radius: int = 12
    ) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.font: pygame.font.Font = font
        self.bg_color: ColorTuple = bg_color
        self.hover_color: ColorTuple = hover_color
        self.text_color: ColorTuple = text_color
        self.border_radius: int = border_radius

        self.is_hovered: bool = False
        self.pressed = False


    def render(self, surface: pygame.Surface) -> None:
        color: ColorTuple = self.hover_color if self.is_hovered else self.bg_color

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        text_surf: pygame.Surface = self.font.render(self.text, True, self.text_color)
        text_rect: pygame.Rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


    def event(self, event: pygame.event.Event):
        self.pressed = False
        if event.type == pygame.MOUSEMOTION:
            pos: Tuple[int, int] = getattr(event, "pos", (0, 0))
            self.is_hovered = self.rect.collidepoint(pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            button: int = getattr(event, "button", 0)
            if button == 1 and self.is_hovered:
                self.pressed = True

    def is_pressed(self) -> bool:
        return self.pressed

