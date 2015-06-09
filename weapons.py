"""
A module for all the possible weapons in the game
"""

import random
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


class WeaponSprite(h.Sprite):
    """
    A weapon's sprite to be shown before being picked up.
    """
    def __init__(self, image, center, weapon):
        """
        Create the weapon sprite with a certain image at a certain spot

        The sprite will move to the ground with the world's gravity, but it
        has a random x component so that it moves away from the chest on spawn.

        :param image: The pygame image associated with the weapon
        :param center: Int tuple representing the spawn point
        :param weapon: The Weapon object associated with this image
        """
        super().__init__()

        self.weapon = weapon

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = center

        self.changex = random.randint(-5, 5)
        self.changey = 0


class Weapon1(Weapon):
    """
    The first weapon
    """

    def __init__(self, center):
        self.image = h.load('weapon.png')
        self.sprite = WeaponSprite(self.image, center, self)

all_weapons = [Weapon1]