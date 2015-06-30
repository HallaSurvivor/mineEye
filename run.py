"""
Run the game.
"""
import logging
import pygame
from config import settings
import gamestates

logger = logging.getLogger('mineEye')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('log.txt')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info('Starting Program')
pygame.init()

screen = pygame.display.set_mode(settings['SCREEN_RESOLUTION'], pygame.FULLSCREEN)
pygame.display.set_caption("mineEye")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

manager = gamestates.GameStateManager()

while not manager.done:
    clock.tick(60)
    if pygame.event.get(pygame.QUIT):
        logger.info('pygame.QUIT - exiting program')
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