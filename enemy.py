"""
Exports the Enemy class that the User actually controls.
"""
import pygame
import constants
import helpers as h


class Enemy(pygame.sprite.Sprite):
    """
    The Enemy that the player fights

    TODO: Add multiple enemy options

    self.image is the picture associated with the enemy, should be 48x48

    self.hp is the Health remaining for the enemy, determines when it dies.

    self.world is the world in which the hero is placed

    self.rect is the Hero's bounding box
        .rect.y is the box's top left corner's y position
        .rect.x is the box's top left corner's x position

    Thanks to those at programarcadegames.com for the basis of this code.
    """
    def __init__(self):
        """
        create the class.
        """
        super().__init__()

        self.image = h.load('badGuy_48.png')

        self.world = None

        self.hp = 100

        self.base_speed = 3
        self.actual_speed = 3

        self.jumping = False
        self.moving_left = False
        self.moving_right = False

        self.rect = self.image.get_rect()
        self.rect.center = constants.CENTER

    def damage(self, amount):
        """
        Reduces the Hero's health based on an event.
        :param amount: Int representing how much damage was taken
        """
        self.hp -= amount