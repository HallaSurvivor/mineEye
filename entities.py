"""
Exports all entities other than weapons and items.

Weapons and Items can be found inside drops.py
"""
import helpers as h


class Projectile(h.Sprite):
    """
    Stores all the data for a projectile.

    This includes an image, a speed, and the damage it does.
    """
    def __init__(self, image, center, changex, changey, damage, owner):
        """
        Create the projectile with a certain image, center, and speed
        :param image: a pygame image to associate with the projectile
        :param center: Int tuple representing the starting point of the projectile
        :param changex: Int representing how quickly the projectile moves in the x direction
        :param changey: Int representing how quickly the projectile moves in the y direction
        :param damage: Int representing the amount of damage the projectile does on contact
        :param owner: The sprite object which spawned the projectile
        """
        super().__init__()

        self.image = image
        self.owner = owner

        self.changex = changex
        self.changey = changey

        self.damage = damage

        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        """
        Change the projectile's position based on changex and changey
        """

        self.rect.x += self.changex
        self.rect.y += self.changey


class Bomb(h.Sprite):
    """
    Stores the data for one of the Hero's bombs.

    This includes an image, a speed, and an explosion radius
    """
    def __init__(self, image, center, changex, changey, radius=128):
        """
        Create the bomb at a certain center, with a certain speed and explosion radius
        :param image: The pygame surface associated with the bomb
        :param center: The spawn location of the bomb
        :param changex: The x component of the bomb's velocity
        :param changey: The y component of the bomb's velocity
        :param radius: Radius (in px) of blocks to destroy/enemies to damage. Defaults to 128 (2 blocks)
        """
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.changex = changex
        self.changey = changey

        self.radius = radius
