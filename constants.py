"""
A place for all the constants to be stored.
"""
import config

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Locations
TOP_LEFT = (0, 0)
TOP_RIGHT = (config.SCREEN_RESOLUTION[0], 0)
BOTTOM_LEFT = (0, config.SCREEN_RESOLUTION[1])
BOTTOM_RIGHT = config.SCREEN_RESOLUTION
CENTER = (config.SCREEN_RESOLUTION[0]/2, config.SCREEN_RESOLUTION[1]/2)