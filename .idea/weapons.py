"""
A module for all the possible weapons in the game
"""

import pygame

class Weapon(object):
    """
    An object for containing the data in each weapon.
    """
    MELEE = 0
    RANGED = 1

    style = MELEE


class WeaponSprite(pygame.sprite.Sprite):
    """
    The sprite associated with a weapon.
    This is what is shown on the ground.
    """
    def __init__(self, image, center):
        """
        Create the weapon sprite with a certain image at a certain spot
        :param image: The pygame image associated with the weapon
        :param center: Int tuple representing the spawn point
        """
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.center = center

