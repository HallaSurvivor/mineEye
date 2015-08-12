"""
Run the game.

MineEye created by Brian Johnson and Christopher Grossack.
2D run and shoot game where you fall down a mineshaft.

Log of stuff that happens is in the aptly named log.txt

If you want the super-verbose I SEE EVERYTHING THE PROGRAM THINKS version,
change logger.setLevel below to logging.DEBUG.
(Fair warning - your game will run SLIGHTLY slower if you do this, as it will
be writing to the file a LOT)

If you want the normal-person I SEE STUFF THAT MATTERS version,
change logger.setLevel below to logging.INFO (default)

Requires:
* Python 3.4
* PyGame
* Pyganim (included)
* PathGetter (included)

Lots of thanks to joel-murielle at http://joel-murielle.perso.sfr.fr/
for the use of PathGetter as a file browser.

Lots of thanks to Al Sweigart at http://inventwithpython.com/pyganim/
for the use of PygAnim to animate sprites more easily

An ENORMOUS thanks to StackExchange. Seriously. We could not have made
it this far without you and your wonderful community.

Much thanks to the Speed Demos Archive forum. We asked stupid
questions about speedrunning, and sent early builds for testing.
The community there is great, and they helped a lot with the
game design.

Feel free to screw around with the code. It SHOULD be fairly
legible/commented/etc. ...I hope.

General outline:
run.py - set up logger, run game loop.
config.py - set up default config file. (overridden by user settings file)
constants.py - if you want to mess with things easily, here's where to start.
hero.py - The hero class and subclasses.
enemy.py - The enemy class and subclasses.
entities.py/drops.py - Bullets, Weapons, Items, the whole lot.
helpers.py - The start of where the magic happens. Load images, redefine sprites, make menus, etc.
gamestates.py - The brunt of what you see that you don't realize you see.
rooms.py - Rooms, walls, enemy calls, movement, updates, etc. If it happens during the actual GAME,
    it probably happens here.

room_options.txt - the definition of all the available rooms' shapes.
                    parsed via JSON
replays/*.txt - a txt file storing the Tick, the Event, and the Event Info to allow
                    functioning replays


Don't post this or modifications anywhere without emailing me first, please. (pssst. if you email me, i'll say yes <3 )
My Email: HallaSurvivor@gmail.com


Source: https://github.com/HallaSurvivor/mineEye
"""
import logging
import pygame
from config import settings
import gamestates

# Create Logger
logger = logging.getLogger('mineEye')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.txt')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info('Starting Program')

# Create the game
pygame.init()

screen = pygame.display.set_mode(settings['SCREEN_RESOLUTION'])
pygame.display.set_caption("mineEye")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

manager = gamestates.GameStateManager()

while not manager.done:
    clock.tick(60)
    if pygame.event.get(pygame.QUIT):
        logger.info('pygame.QUIT - exiting program')
        manager.done = True

    # if screen.get_flags() & pygame.FULLSCREEN != pygame.FULLSCREEN:
    #     for event in pygame.event.get(pygame.VIDEORESIZE):
    #         screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
    #         settings['SCREEN_RESOLUTION'] = event.dict['size']
    #         settings['WIDTH'] = event.dict['w']
    #         settings['HEIGHT'] = event.dict['h']

    if not manager.replay:
        manager.state.handle_events(pygame.event.get())
    else:
        logger.debug('replay event', manager.state.tick_count, manager.state.event_list)
        manager.state.handle_events(manager.state.event_list)

    manager.state.update()
    manager.state.draw(screen)

    pygame.display.flip()