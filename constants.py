"""
A place for all the constants to be stored.
"""
from config import settings
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Locations
TOP_LEFT = (0, 0)
TOP_RIGHT = (settings['SCREEN_RESOLUTION'][0], 0)
BOTTOM_LEFT = (0, settings['SCREEN_RESOLUTION'][1])
BOTTOM_RIGHT = settings['SCREEN_RESOLUTION']
CENTER = (settings['SCREEN_RESOLUTION'][0]/2, settings['SCREEN_RESOLUTION'][1]/2)