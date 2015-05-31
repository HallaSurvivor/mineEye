"""
A place to store things that the user can modify.
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

#Unless...
# if not os.path.exists('settings'):
#     settings_dict = {}
#     exclude = ['os', 'pickle', 'pygame', 'settings_dict', 'exclude']
#     for item in [item for item in dir() if not item.startswith('__') and item not in exclude]:
#         settings_dict[item] = locals()[item]
#
#     f = open('settings', 'wb')
#     f.write(pickle.dumps(settings_dict))
#     f.close()
#
# else:
#     f = open('settings', 'rb')
#     settings_dict = pickle.loads(f.read())
#     f.close()
#     for key in settings_dict.keys():
#         locals()[key] = settings_dict[key]