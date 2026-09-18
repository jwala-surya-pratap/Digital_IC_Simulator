from enum import Enum
import pygame
import sys

from ui import *

class UiState(Enum):
    WORLD_VIEW = 1

class App:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_FPS = 60


    def __init__(self) -> None:
        pygame.init()

        self.display = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # === [UI] ===
        # Fonts
        bold_font = pygame.font.Font("assets/fonts/JetBrainsMono-Bold.ttf")


        self.ui_state = UiState.WORLD_VIEW
        self.ui = Ui()

        self.ui.add_element("add_button", Button(self.WINDOW_WIDTH - 60, self.WINDOW_HEIGHT - 60, 50, 50, "+", bold_font))

    def event(self, event: pygame.event.Event):
        self.ui.event(event)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.display)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.event(event)

            self.update()

            self.display.fill((69, 69, 69))
            self.render()
            pygame.display.update()
            self.clock.tick(self.WINDOW_FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.run()
