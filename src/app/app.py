import pygame
from sys import exit
from core.manager import ComponentManager


class App:
    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()

        self.manager = ComponentManager()


    def event(self, event: pygame.Event):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                self.event(event)

            self.surface.fill((69, 69, 69))
            self.update()
            self.render()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    app = App()
    app.run()
