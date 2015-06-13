"""
A module for all the possible weapons in the game
"""

import random
import helpers as h

MELEE = 0
RANGED = 1

class Weapon(object):
    """
    An object for containing the data in each weapon.
    """
    style = MELEE

    image = None
    sprite = None
    top_sprite = None

    def attack(self):
        """
        A blank method meant to be overwritten in each weapon.
        """
        pass


class WeaponSprite(h.Sprite):
    """
    A weapon's sprite to be shown before being picked up.
    """
    is_weapon = True
    is_item = False

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


class TopSprite(h.Sprite):
    """
    The sprite shown in the HUD to tell the user which weapons are equipped.
    """
    def __init__(self, image, weapon):
        super().__init__()

        self.weapon = weapon
        self.image = image

        self.rect = self.image.get_rect()


class Weapon1(Weapon):
    """
    The first weapon
    """
    style = MELEE

    def __init__(self, center):
        self.sprite = WeaponSprite(h.load('weapon.png'), center, self)
        self.top_sprite = TopSprite(h.load('top_weapon.png'), self)

all_weapons = [Weapon1]