from enum import Enum
import pygame
import sys

from ui import Button

class UiState(Enum):
    WORLD_VIEW = 1

class ComponentData:
    x: int = 0
    y: int = 0

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class App:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_FPS = 60


    def __init__(self) -> None:
        pygame.init()

        self.display = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # === [UI] ===
        self.ui_state = UiState.WORLD_VIEW

        # Fonts
        bold_font = pygame.font.Font("assets/fonts/JetBrainsMono-Bold.ttf")

        self.add_button = Button(10, 10, 50, 50, "+", bold_font)

    def event(self, event: pygame.event.Event):
        self.add_button.event(event)

        match self.ui_state:
            case UiState.WORLD_VIEW:
                if self.add_button.is_pressed():
                    pass


    def update(self):
        pass

    def render(self):
        self.add_button.render(self.display)

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
