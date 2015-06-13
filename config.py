"""
Default values for things the user can modify in game.
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