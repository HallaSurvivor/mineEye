"""
Run the game.
"""
import pygame
from config import settings
import gamestates

pygame.init()
screen = pygame.display.set_mode(settings['SCREEN_RESOLUTION'])
pygame.display.set_caption("mineEye")
clock = pygame.time.Clock()

manager = gamestates.GameStateManager()

while not manager.done:
    clock.tick(60)

    if pygame.event.get(pygame.QUIT):
        manager.done = True

    manager.state.handle_events(pygame.event.get())
    manager.state.update()
    manager.state.draw(screen)

    pygame.display.flip()