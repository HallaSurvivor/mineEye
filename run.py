"""
Run the game.
"""
import pygame
from config import settings
import gamestates

pygame.init()
screen = pygame.display.set_mode(settings['SCREEN_RESOLUTION'], pygame.FULLSCREEN)
pygame.display.set_caption("mineEye")
clock = pygame.time.Clock()

manager = gamestates.GameStateManager()

while not manager.done:
    clock.tick(60)
    if pygame.event.get(pygame.QUIT):
        manager.done = True

    if screen.get_flags() & pygame.FULLSCREEN != pygame.FULLSCREEN:
        for event in pygame.event.get(pygame.VIDEORESIZE):
            screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            settings['SCREEN_RESOLUTION'] = event.dict['size']
            settings['WIDTH'] = event.dict['w']
            settings['HEIGHT'] = event.dict['h']

    manager.state.handle_events(pygame.event.get())
    manager.state.update()
    manager.state.draw(screen)

    pygame.display.flip()