"""
Default values for things the user can modify in game.
"""
import os
import pickle
import pygame

#Defaults:
SCREEN_RESOLUTION = (1366, 768)

PLAY_MUSIC = False

UP = pygame.K_w
LEFT = pygame.K_a
DOWN = pygame.K_s
RIGHT = pygame.K_d

BOMB = pygame.K_b

PAUSE = pygame.K_ESCAPE

settings = {}
exclude = ['os', 'pickle', 'pygame', 'settings_dict', 'exclude']
for item in [item for item in dir() if not item.startswith('__') and item not in exclude]:
    settings[item] = locals()[item]

#Unless...
if not os.path.exists('settings'):
    f = open('settings', 'wb')
    f.write(pickle.dumps(settings))
    f.close()
else:
    f = open('settings', 'rb')
    settings = pickle.loads(f.read())
    f.close()