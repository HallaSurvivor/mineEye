"""
A place for all the constants to be stored.

Uses the settings dictionary in order to automatically calculate some values based on screen resolution.
"""
from config import settings

SCREEN_SIZE = settings['SCREEN_RESOLUTION']
WIDTH = SCREEN_SIZE[0]
HEIGHT = SCREEN_SIZE[1]

HP_BACKGROUND_SIZE = (1/6 * WIDTH, 48)
HP_BAR_SIZE = (1/6 * WIDTH - 4, 44)

# Locations
TOP_LEFT = (0, 0)
TOP_RIGHT = (WIDTH, 0)
BOTTOM_LEFT = (0, HEIGHT)
BOTTOM_RIGHT = (WIDTH, HEIGHT)
CENTER = (WIDTH/2, HEIGHT/2)

HP_BACKGROUND_POS = (2, 2)
HP_BAR_POS = (4, 4)

BOMB_POS = (0, 64)
MELEE_POS = (144, 64)
RANGED_POS = (192, 64)

SEED_POS = (.85*WIDTH, .95*HEIGHT)


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Enums
MELEE = 0
RANGED = 1


def calc_sizes():
    global WIDTH, HEIGHT, HP_BACKGROUND_SIZE, HP_BAR_SIZE, \
    TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, CENTER, \
    HP_BACKGROUND_POS, HP_BAR_POS, BOMB_POS, MELEE_POS, RANGED_POS, \
    SEED_POS

    SCREEN_SIZE = settings['SCREEN_RESOLUTION']
    WIDTH = SCREEN_SIZE[0]
    HEIGHT = SCREEN_SIZE[1]

    HP_BACKGROUND_SIZE = (1/6 * WIDTH, 48)
    HP_BAR_SIZE = (1/6 * WIDTH - 4, 44)

    # Locations
    TOP_LEFT = (0, 0)
    TOP_RIGHT = (WIDTH, 0)
    BOTTOM_LEFT = (0, HEIGHT)
    BOTTOM_RIGHT = (WIDTH, HEIGHT)
    CENTER = (WIDTH/2, HEIGHT/2)

    HP_BACKGROUND_POS = (2, 2)
    HP_BAR_POS = (4, 4)

    BOMB_POS = (0, 64)
    MELEE_POS = (144, 64)
    RANGED_POS = (192, 64)

    SEED_POS = (.85*WIDTH, .95*HEIGHT)