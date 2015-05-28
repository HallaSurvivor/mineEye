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

    self.change_x is the Hero's movement speed in the x direction
    self.change_y is the Hero's movement speed in the y direction

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

        self.hp = 5000

        self.change_x = 0
        self.change_y = 0

        self.rect = self.image.get_rect()
        self.rect.center = constants.CENTER

    def damage(self, amount):
        """
        Reduces the Hero's health based on an event.
        :param amount: Int representing how much damage was taken
        """
        self.hp -= amount
