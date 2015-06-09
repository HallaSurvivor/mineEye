"""
Exports entities that get spawned in over time

The only exceptions are weapons and items,
The entities associated with them are stored in their respective files.

Exports:

Projectile
Bombs
"""
import helpers as h


class Projectile(h.Sprite):
    """
    Stores all the data for a projectile.
    """
    def __init__(self, image, center, changex, changey, damage):
        """
        Create the projectile with a certain image, center, and speed
        :param image: a pygame image to associate with the projectile
        :param center: Int tuple representing the starting point of the projectile
        :param changex: Int representing how quickly the projectile moves in the x direction
        :param changey: Int representing how quickly the projectile moves in the y direction
        :param damage: Int representing the amount of damage the projectile does on contact
        """
        super().__init__()

        self.image = image

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
    """
    def __init__(self, image, center, changex, changey, radius=128, controlled=False):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = center

        self.changex = changex
        self.changey = changey

        self.radius = radius

        self.controlled = controlled

