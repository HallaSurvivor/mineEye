"""
Default values for things the user can modify in game.

This file automatically creates a dictionary named settings that
stores all of the settings that other modules reference.

It also creates a new file named "settings" that stores a
pickled version of this dictionary.

The settings file will override the dictionary that is created,
and is re created every time the user changes settings. This way,
user changes take place immediately, and also last permanently
without changing the default settings (seen below).

Because of this, any changes made to this file will not take place
until the old settings file is deleted.

Likewise, any options that you add will cause a KeyError until the
settings file that does not include the new options is deleted.

>> DEBUG <<
if True -
lets the user go into God Mode
    * Infinite health
    * Super high jumps
    * Infinite ammo

This is meant to test world generation and enemy effects
in a way that allows the user to remain alive indefinitely.
"""
import os
import logging
import pickle
import pygame
module_logger = logging.getLogger('mineEye.config')

#Defaults:
SCREEN_RESOLUTION = (1366, 768)

DEBUG = True

SHOW_NODES = False

PLAY_MUSIC = True
PLAY_SFX = True

UP = pygame.K_w
LEFT = pygame.K_a
DOWN = pygame.K_s
RIGHT = pygame.K_d

BOMB = pygame.K_SPACE

PAUSE = pygame.K_p

WIDTH = SCREEN_RESOLUTION[0]
HEIGHT = SCREEN_RESOLUTION[1]


try:
    f = open('settings', 'rb')
    settings = pickle.loads(f.read())
    f.close()

except:
    module_logger.info('Created new settings dictionary')
    settings = {}
    exclude = ['os', 'pickle', 'pygame', 'logging', 'exclude', 'settings', 'module_logger']
    for item in [item for item in dir() if not item.startswith('__') and item not in exclude]:
        settings[item] = locals()[item]

    f = open('settings', 'wb')
    f.write(pickle.dumps(settings))
    f.close()

settings['GOD MODE'] = False
settings['SHOW_NODES'] = SHOW_NODES
settings['DEBUG'] = DEBUG