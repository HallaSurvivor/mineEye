"""
A module for all the possible weapons and items in the game
"""

import random
import helpers as h
import constants as c


class Weapon(object):
    """
    An object for containing the data in each weapon.
    """
    style = None
    power = 0
    range = 0
    arcs = False
    sprite_to_load = ''
    top_sprite_to_load = ''

    image = None
    sprite = None
    top_sprite = None

    def __init__(self, center):
        self.sprite = DropSprite(h.load(self.sprite_to_load), center, self)
        self.top_sprite = TopSprite(h.load(self.top_sprite_to_load), self)


class DropSprite(h.Sprite):
    """
    A sprite to be shown while the drop is in the world.
    """
    is_weapon = True
    is_item = False

    def __init__(self, image, center, drop):
        """
        Create the sprite with a certain image at a certain spot

        The sprite will move to the ground with the world's gravity, but it
        has a random x component so that it moves away from the chest on spawn.

        :param image: The pygame image associated with the weapon
        :param center: Int tuple representing the spawn point
        :param weapon: The Weapon object associated with this image
        """
        super().__init__()

        self.drop = drop

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
    style = c.MELEE
    power = 50
    range = 128

    sprite_to_load = 'weapon.png'
    top_sprite_to_load = 'top_weapon.png'

    def __init__(self, center):
        super().__init__(center)


class Weapon2(Weapon):
    """
    Another weapon
    """
    style = c.MELEE
    power = 100
    range = 64

    sprite_to_load = 'weapon2.png'
    top_sprite_to_load = 'top_weapon2.png'

    def __init__(self, center):
        super().__init__(center)

all_weapons = [Weapon1, Weapon2]