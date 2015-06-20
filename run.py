"""
Run the game.
"""
import pygame
from config import settings
from constants import calc_sizes, SCREEN_SIZE
import gamestates

pygame.init()
screen = pygame.display.set_mode(settings['SCREEN_RESOLUTION'], pygame.RESIZABLE)
pygame.display.set_caption("mineEye")
clock = pygame.time.Clock()

manager = gamestates.GameStateManager()

while not manager.done:
    clock.tick(60)
    if pygame.event.get(pygame.QUIT):
        manager.done = True

    for event in pygame.event.get(pygame.VIDEORESIZE):
        screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
        settings['SCREEN_RESOLUTION'] = event.dict['size']
        calc_sizes()
        print(SCREEN_SIZE)

    manager.state.handle_events(pygame.event.get())
    manager.state.update()
    manager.state.draw(screen)

    pygame.display.flip()