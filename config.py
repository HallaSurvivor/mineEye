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
"""
import os
import pickle
import pygame

#Defaults:
SCREEN_RESOLUTION = (1366, 768)

PLAY_MUSIC = True
PLAY_SFX = False

UP = pygame.K_w
LEFT = pygame.K_a
DOWN = pygame.K_s
RIGHT = pygame.K_d

MELEE = pygame.K_j
RANGED = pygame.K_k

BOMB = pygame.K_SPACE

PAUSE = pygame.K_ESCAPE


if not os.path.exists('settings'):
    settings = {}
    exclude = ['os', 'pickle', 'pygame', 'exclude']
    for item in [item for item in dir() if not item.startswith('__') and item not in exclude]:
        settings[item] = locals()[item]

    f = open('settings', 'wb')
    f.write(pickle.dumps(settings))
    f.close()

else:
    f = open('settings', 'rb')
    settings = pickle.loads(f.read())
    f.close()