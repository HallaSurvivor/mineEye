"""
A place to store things that the user can modify.
"""
import pygame

SCREEN_RESOLUTION = (1024, 768)

PLAY_MUSIC = False

KEY_CANCELING = True       # If TRUE, pushing Left while holding Right will make you move left.
                            # If FALSE, pushing Left while holding Right will make you stand still.

UP = pygame.K_UP
LEFT = pygame.K_LEFT
DOWN = pygame.K_DOWN
RIGHT = pygame.K_RIGHT

PAUSE = pygame.K_ESCAPE