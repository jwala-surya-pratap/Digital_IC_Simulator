from __future__ import annotations

from typing import Callable, Type
import pygame

from core.ICs import IC
from ui.ui_element import UiElement


class AddICMenu(UiElement):
    """
    Modal menu for selecting and adding IC chips to the circuit board.
    Dynamically loads all IC classes registered with the base IC class,
    future-proofing the system so any newly authored IC class automatically
    appears in this menu without modifying UI code.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        on_select: Callable[[Type[IC]], None],
        on_close: Callable[[], None],
    ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.small_font = small_font
        self.on_select = on_select
        self.on_close = on_close

        # Dynamically query all registered IC classes
        self.ic_classes = IC.get_registered_classes()

        # Modal dimensions
        self.dialog_width = 520
        self.dialog_height = 480
        self.dialog_x = (screen_width - self.dialog_width) // 2
        self.dialog_y = (screen_height - self.dialog_height) // 2

        self.scroll_offset: int = 0
        self.card_height = 56
        self.card_spacing = 8
        self.visible_height = self.dialog_height - 90  # Area below title bar

        self.hovered_index: int = -1
        self.close_hovered: bool = False

    @property
    def dialog_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.dialog_x, self.dialog_y, self.dialog_width, self.dialog_height
        )

    @property
    def close_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.dialog_x + self.dialog_width - 34, self.dialog_y + 14, 22, 22
        )

    @property
    def max_scroll(self) -> int:
        total_content = len(self.ic_classes) * (self.card_height + self.card_spacing)
        return max(0, total_content - self.visible_height + 20)

    def get_card_rect(self, index: int) -> pygame.Rect:
        card_w = self.dialog_width - 36
        card_h = self.card_height
        card_x = self.dialog_x + 18
        card_y = (
            self.dialog_y
            + 68
            + index * (self.card_height + self.card_spacing)
            - self.scroll_offset
        )
        return pygame.Rect(card_x, card_y, card_w, card_h)

    def event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(
                0, min(self.max_scroll, self.scroll_offset - event.y * 28)
            )

        elif event.type == pygame.MOUSEMOTION:
            pos = getattr(event, "pos", (0, 0))
            self.close_hovered = self.close_rect.collidepoint(pos)
            self.hovered_index = -1

            # Only hover if inside dialog content area
            content_rect = pygame.Rect(
                self.dialog_x, self.dialog_y + 60, self.dialog_width, self.visible_height
            )
            if content_rect.collidepoint(pos):
                for i in range(len(self.ic_classes)):
                    if self.get_card_rect(i).collidepoint(pos):
                        self.hovered_index = i
                        break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = getattr(event, "pos", (0, 0))

            # Click close button
            if self.close_rect.collidepoint(pos):
                self.on_close()
                return

            # Click an IC card
            content_rect = pygame.Rect(
                self.dialog_x, self.dialog_y + 60, self.dialog_width, self.visible_height
            )
            if content_rect.collidepoint(pos):
                for i, ic_cls in enumerate(self.ic_classes):
                    if self.get_card_rect(i).collidepoint(pos):
                        self.on_select(ic_cls)
                        self.on_close()
                        return

            # Click outside dialog to dismiss
            if not self.dialog_rect.collidepoint(pos):
                self.on_close()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_close()

    def render(self, surface: pygame.Surface):
        # 1. Dark semi-transparent backdrop overlay
        backdrop = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        backdrop.fill((0, 0, 0, 160))
        surface.blit(backdrop, (0, 0))

        # 2. Dialog box
        pygame.draw.rect(surface, (22, 26, 34), self.dialog_rect, border_radius=12)
        pygame.draw.rect(
            surface, (55, 65, 81), self.dialog_rect, width=2, border_radius=12
        )

        # 3. Header title and subtitle
        title_surf = self.font.render("Select Integrated Circuit (IC)", True, (243, 244, 246))
        surface.blit(title_surf, (self.dialog_x + 20, self.dialog_y + 14))

        sub_surf = self.small_font.render(
            f"Choose from {len(self.ic_classes)} available real-life IC classes • Scroll for more",
            True,
            (148, 163, 184),
        )
        surface.blit(sub_surf, (self.dialog_x + 20, self.dialog_y + 36))

        # 4. Close [x] button
        close_bg = (239, 68, 68) if self.close_hovered else (45, 52, 65)
        close_fg = (255, 255, 255) if self.close_hovered else (156, 163, 175)
        pygame.draw.rect(surface, close_bg, self.close_rect, border_radius=4)
        x_surf = self.small_font.render("×", True, close_fg)
        surface.blit(x_surf, x_surf.get_rect(center=self.close_rect.center))

        # 5. Render IC cards clipped inside scroll area
        clip_rect = pygame.Rect(
            self.dialog_x + 10,
            self.dialog_y + 60,
            self.dialog_width - 20,
            self.visible_height,
        )
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        for i, ic_cls in enumerate(self.ic_classes):
            card_rect = self.get_card_rect(i)

            # Skip cards completely outside visible area
            if card_rect.bottom < clip_rect.top or card_rect.top > clip_rect.bottom:
                continue

            is_hover = self.hovered_index == i

            card_bg = (38, 46, 60) if is_hover else (28, 34, 44)
            card_border = (96, 165, 250) if is_hover else (48, 58, 74)

            pygame.draw.rect(surface, card_bg, card_rect, border_radius=8)
            pygame.draw.rect(
                surface, card_border, card_rect, width=2 if is_hover else 1, border_radius=8
            )

            # Chip badge (styled like a mini IC package)
            badge_rect = pygame.Rect(card_rect.x + 10, card_rect.y + 10, 64, 36)
            badge_bg = (37, 99, 235) if is_hover else (40, 50, 66)
            pygame.draw.rect(surface, badge_bg, badge_rect, border_radius=6)
            pygame.draw.rect(surface, (70, 85, 110), badge_rect, width=1, border_radius=6)

            name_surf = self.font.render(ic_cls.chip_name, True, (255, 255, 255))
            surface.blit(name_surf, name_surf.get_rect(center=badge_rect.center))

            # Gate name & description
            label_surf = self.small_font.render(
                f"{ic_cls.type_name} ({ic_cls.total_pins}-pin DIP)", True, (243, 244, 246)
            )
            surface.blit(label_surf, (card_rect.x + 84, card_rect.y + 10))

            desc_surf = self.small_font.render(ic_cls.description, True, (156, 163, 175))
            surface.blit(desc_surf, (card_rect.x + 84, card_rect.y + 30))

            # Add icon on the right
            add_txt = "+ ADD" if is_hover else "+"
            add_surf = self.small_font.render(
                add_txt, True, (96, 165, 250) if is_hover else (107, 114, 128)
            )
            surface.blit(
                add_surf,
                add_surf.get_rect(right=card_rect.right - 14, centery=card_rect.centery),
            )

        surface.set_clip(old_clip)

        # 6. Scrollbar indicator if scrollable
        if self.max_scroll > 0:
            track_rect = pygame.Rect(
                self.dialog_x + self.dialog_width - 12,
                self.dialog_y + 64,
                4,
                self.visible_height - 8,
            )
            pygame.draw.rect(surface, (45, 52, 65), track_rect, border_radius=2)

            thumb_height = max(
                20, int(track_rect.height * (self.visible_height / (self.visible_height + self.max_scroll)))
            )
            thumb_y = track_rect.y + int(
                (track_rect.height - thumb_height) * (self.scroll_offset / self.max_scroll)
            )
            thumb_rect = pygame.Rect(track_rect.x, thumb_y, 4, thumb_height)
            pygame.draw.rect(surface, (96, 165, 250), thumb_rect, border_radius=2)
