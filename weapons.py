"""
A module for all the possible weapons in the game
"""

import pygame
import helpers as h


class Weapon(object):
    """
    An object for containing the data in each weapon.
    """
    MELEE = 0
    RANGED = 1
    style = MELEE

    image = None
    sprite = None


class WeaponSprite(pygame.sprite.Sprite):
    """
    The sprite associated with a weapon.
    This is what is shown on the ground.
    """
    def __init__(self, image, center, weapon):
        """
        Create the weapon sprite with a certain image at a certain spot
        :param image: The pygame image associated with the weapon
        :param center: Int tuple representing the spawn point
        :param weapon: The Weapon object associated with this image
        """
        super().__init__()

        self.weapon = weapon

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = center


class Weapon1(Weapon):
    """
    The first weapon
    """

    def __init__(self, center):
        self.image = h.load('weapon.png')
        self.sprite = WeaponSprite(self.image, center, self)

all_weapons = [Weapon1]