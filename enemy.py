"""
Exports the Enemy class that the User actually controls.
"""
import pygame
import constants
import helpers as h


class Enemy(pygame.sprite.Sprite):
    """
    An Enemy superclass meant to be subclassed by individual enemies.
    """

    hp = 100
    speed = 3

    def __init__(self):
        """
        create the class.
        note damage_player_on_touch means that when the player is hitting the bad guy damage is done. This would be true of a bwarler type chractor
        """
        super().__init__()

        self.image = pygame.Surface((48, 48))

        self.world = None

        self.current_hp = self.hp


        self.moving_left = False
        self.moving_right = False


        self.damage_player_on_touch = True

        self.jumping = False
        self.moving_left = False
        self.moving_right = False

        self.rect = self.image.get_rect()

    def damage(self, amount):
        """
        Reduces the Enemy's health based on an event.
        :param amount: Int representing how much damage was taken
        """
        self.current_hp -= amount

    def movex(self, xspeed):
        """
        Move the enemy by a certain amount in the x direction.
        :param xspeed: Int representing the change in x direction
        """
        self.rect.x += xspeed

    def movey(self, yspeed):
        """
        Move the enemy by a certain amount in the x direction.
        :param yspeed:  Int representing the change in y direction
        """
        self.rect.y += yspeed


class Enemy1(Enemy):
    """
    A basic enemy
    """

    def __init__(self):
        super().__init__()

        self.image = h.load('badGuy.png')
