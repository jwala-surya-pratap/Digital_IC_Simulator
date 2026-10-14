from __future__ import annotations

from enum import Enum
from pathlib import Path
import sys
import pygame

from core.ICs import IC, IC7404, IC7408, AVAILABLE_ICS
from core.manager import Manager
from ui import Ui
from ui.elements.button import Button
from ui.elements.canvas import CircuitCanvas
from ui.elements.menu import AddICMenu


class UiState(Enum):
    WORLD_VIEW = 1


class App:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_FPS = 60

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Digital IC Simulator")

        self.display = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # === [FONTS] ===
        font_file = Path("assets/fonts/JetBrainsMono-Bold.ttf")
        if font_file.exists():
            self.title_font = pygame.font.Font(str(font_file), 17)
            self.bold_font = pygame.font.Font(str(font_file), 15)
            self.normal_font = pygame.font.Font(str(font_file), 13)
            self.small_font = pygame.font.Font(str(font_file), 11)
        else:
            self.title_font = pygame.font.SysFont("monospace", 17, bold=True)
            self.bold_font = pygame.font.SysFont("monospace", 15, bold=True)
            self.normal_font = pygame.font.SysFont("monospace", 13)
            self.small_font = pygame.font.SysFont("monospace", 11)

        self.status_message = (
            "Click input pins to toggle 0/1 • Drag OUT/VCC to IN to wire • Right-click to disconnect"
        )

        # === [UI SYSTEM] ===
        self.ui_state = UiState.WORLD_VIEW
        self.ui = Ui()

        # 1. Circuit Canvas
        self.canvas = CircuitCanvas(
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            font=self.bold_font,
            small_font=self.small_font,
            status_callback=self.on_status_update,
        )
        self.ui.add_element("canvas", self.canvas)

        # 2. Add IC Button (Bottom-Right FAB)
        self.add_button = Button(
            x=self.WINDOW_WIDTH - 64,
            y=self.WINDOW_HEIGHT - 64,
            width=48,
            height=48,
            text="+",
            font=self.title_font,
            bg_color=(34, 197, 94),
            hover_color=(74, 222, 128),
            text_color=(10, 30, 15),
            border_radius=24,
            on_click=self.open_add_menu,
        )
        self.ui.add_element("add_button", self.add_button)

        # 3. Top Toolbar Buttons
        self.top_add_button = Button(
            x=self.WINDOW_WIDTH - 240,
            y=8,
            width=110,
            height=32,
            text="+ Add IC",
            font=self.normal_font,
            bg_color=(37, 99, 235),
            hover_color=(59, 130, 246),
            text_color=(255, 255, 255),
            border_radius=6,
            on_click=self.open_add_menu,
        )
        self.ui.add_element("top_add_button", self.top_add_button)

        self.clear_button = Button(
            x=self.WINDOW_WIDTH - 120,
            y=8,
            width=100,
            height=32,
            text="Clear",
            font=self.normal_font,
            bg_color=(55, 65, 81),
            hover_color=(239, 68, 68),
            text_color=(229, 231, 235),
            border_radius=6,
            on_click=self.canvas.clear_all,
        )
        self.ui.add_element("clear_button", self.clear_button)

        # 4. Add IC Modal (initially inactive)
        self.add_menu: AddICMenu | None = None

        # Pre-populate demo ICs (7404 NOT and 7408 AND)
        self.setup_default_circuit()

    def setup_default_circuit(self) -> None:
        """Place an initial NOT and AND gate on the board to demonstrate immediately."""
        self.canvas.add_ic(IC7404, (180, 140))
        self.canvas.add_ic(IC7408, (580, 140))

    def on_status_update(self, message: str) -> None:
        self.status_message = message

    def open_add_menu(self) -> None:
        self.add_menu = AddICMenu(
            screen_width=self.WINDOW_WIDTH,
            screen_height=self.WINDOW_HEIGHT,
            font=self.bold_font,
            small_font=self.small_font,
            on_select=self.on_select_ic_from_menu,
            on_close=self.close_add_menu,
        )

    def close_add_menu(self) -> None:
        self.add_menu = None

    def on_select_ic_from_menu(self, ic_cls: type[IC]) -> None:
        self.canvas.add_ic(ic_cls)
        self.close_add_menu()

    def event(self, event: pygame.event.Event):
        # If modal menu is open, it captures user events exclusively
        if self.add_menu is not None:
            self.add_menu.event(event)
            return

        # Otherwise forward to UI elements
        self.ui.event(event)

    def update(self):
        self.ui.update()

    def render_top_bar(self):
        """Render top dark navigation bar with title and signal legends."""
        bar_rect = pygame.Rect(0, 0, self.WINDOW_WIDTH, 48)
        pygame.draw.rect(self.display, (18, 21, 27), bar_rect)
        pygame.draw.line(self.display, (45, 52, 65), (0, 48), (self.WINDOW_WIDTH, 48), 1)

        # App Logo & Title
        title_surf = self.title_font.render("DIGITAL IC SIMULATOR", True, (240, 245, 255))
        self.display.blit(title_surf, (20, 14))

        # Status / Instructions
        status_surf = self.normal_font.render(self.status_message, True, (156, 163, 175))
        self.display.blit(status_surf, (300, 16))

        # Render top bar buttons
        self.top_add_button.render(self.display)
        self.clear_button.render(self.display)

    def render_legend(self):
        """Render bottom-left logic state legend."""
        legend_rect = pygame.Rect(16, self.WINDOW_HEIGHT - 36, 320, 26)
        pygame.draw.rect(self.display, (22, 26, 33), legend_rect, border_radius=4)
        pygame.draw.rect(self.display, (45, 52, 65), legend_rect, width=1, border_radius=4)

        # High indicator dot
        pygame.draw.circle(self.display, (34, 197, 94), (28, self.WINDOW_HEIGHT - 23), 6)
        h_surf = self.small_font.render("HIGH (1)", True, (209, 213, 219))
        self.display.blit(h_surf, (38, self.WINDOW_HEIGHT - 30))

        # Low indicator dot
        pygame.draw.circle(self.display, (75, 85, 99), (120, self.WINDOW_HEIGHT - 23), 6)
        l_surf = self.small_font.render("LOW (0)", True, (209, 213, 219))
        self.display.blit(l_surf, (130, self.WINDOW_HEIGHT - 30))

        # Wires count
        wire_cnt = len(self.canvas.wires)
        ic_cnt = len(self.canvas.ic_elements)
        stats_surf = self.small_font.render(
            f"ICs: {ic_cnt} • Wires: {wire_cnt}", True, (156, 163, 175)
        )
        self.display.blit(stats_surf, (204, self.WINDOW_HEIGHT - 30))

    def render(self):
        # 1. Canvas and circuit elements
        self.canvas.render(self.display)

        # 2. Add FAB Button
        self.add_button.render(self.display)

        # 3. Top Toolbar
        self.render_top_bar()

        # 4. Bottom Legend
        self.render_legend()

        # 5. Modal Menu if open
        if self.add_menu is not None:
            self.add_menu.render(self.display)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.event(event)

            self.update()

            self.display.fill((30, 34, 42))
            self.render()
            pygame.display.update()
            self.clock.tick(self.WINDOW_FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.run()
