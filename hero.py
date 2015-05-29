"""
Exports the Hero class that the User actually controls.
"""
import pygame
import constants
import helpers as h


class Hero(pygame.sprite.Sprite):
    """
    The Hero that the player controls

    TODO: Add multiple hero options

    self.image is the picture associated with the Hero, should be 48x48

    self.hp is the Health remaining for the Hero.

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

        self.image = h.load('herosprite.png')

        self.world = None

        self.hp = 5000

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