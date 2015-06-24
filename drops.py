"""
A module for all the possible weapons and items in the game.

Exports 2 lists, all_weapons and all_items that are used
to randomly generate chests inside of rooms.py
"""

import random
import helpers as h
import constants as c


class Weapon(object):
    """
    An object subclassed by each weapon.

    style:
        Either c.MELEE or c.RANGED
        This changes the way that the Hero uses a given weapon,
        as well as which attributes matter.

    power:
        value showing how much damage the weapon does when it hits

    range:
        value representing the range of a melee weapon
        Any enemy whose center is less than the range
        from the hero is damaged

    arcs:
        boolean for if a ranged weapon arcs due to gravity
        True - weapon will arc
        False - weapon will travel in a straight line

    sprite_to_load:
        a string showing which sprite should be loaded as
        the sprite displayed in the world, such as after
        opening a chest.
        Passed to h.load()

        This is used instead of simply using h.load without
        instantiating so as to avoid an error with using
        pygame sprites before initializing pygame.

    top_sprite_to_load:
        a string showing which sprite should be loaded as
        the sprite displayed in the HUD
        Passed to h.load()

        This is used instead of simply using h.load without
        instantiating so as to avoid an error with using
        pygame sprites before initializing pygame.

    sprite/top_sprite:
        The actual pygame sprites that are associated with
        the image.
        sprite is the sprite in the world
        top_sprite is the sprite in the HUD

        These are created automatically in __init__(), however
        they are included in case of an exception, such as
        creating a sprite dynamically.
    """
    name = ""
    style = None
    power = 0
    range = 0
    arcs = False
    sprite_to_load = ''
    top_sprite_to_load = ''

    sprite = None
    top_sprite = None

    def __init__(self, center):
        self.sprite = DropSprite(h.load(self.sprite_to_load), center, self)
        self.sprite.is_weapon = True
        self.top_sprite = TopSprite(h.load(self.top_sprite_to_load), self)


class DropSprite(h.Sprite):
    """
    A sprite to be shown while the drop is in the world.

    is_weapon/is_item:
        booleans showing the nature of the drop.
        The appropriate flag is set to True when created.
    """
    is_weapon = False
    is_item = False

    def __init__(self, image, center, drop):
        """
        Create the sprite with a certain image at a certain spot

        The sprite will move to the ground with the world's gravity, but it
        has a random x component so that it moves away from the chest on spawn.

        :param image: The pygame image associated with the weapon
        :param center: Int tuple representing the spawn point
        :param drop: The Weapon/Item object associated with this image
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
    name = 'weapon 1'
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
    name = 'weapon 2'
    style = c.MELEE
    power = 100
    range = 64

    sprite_to_load = 'weapon2.png'
    top_sprite_to_load = 'top_weapon2.png'

    def __init__(self, center):
        super().__init__(center)

all_weapons = [Weapon1, Weapon2]