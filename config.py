"""
Default values for things the user can modify in game.
"""
import os
import pickle
import pygame

#Defaults:
SCREEN_RESOLUTION = (1366, 768)

PLAY_MUSIC = False

KEY_CANCELING = True       # If TRUE, pushing Left while holding Right will make you move left.
                            # If FALSE, pushing Left while holding Right will make you stand still.

UP = pygame.K_UP
LEFT = pygame.K_LEFT
DOWN = pygame.K_DOWN
RIGHT = pygame.K_RIGHT

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