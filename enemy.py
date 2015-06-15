"""
Exports the Enemy classes that the Hero has to battle.
"""
from math import hypot
import pygame
import helpers as h
import constants as c
import entities


class Enemy(h.Sprite):
    """
    An Enemy superclass meant to be subclassed by individual enemies.

    hp:
        the health the enemy has

    speed:
        the enemy's speed in px/tick

    contact_damage:
        the amount of damage the enemy does when the player touches it.

    is_melee/is_ranged:
        A flag for how the enemy damages the user.
        The correct flag is set to True in the individual Enemy subclass

    clips:
        boolean for if the enemy clips.
        True if it doesn't move through walls
        False if it does move through walls

    attack_range:
        the number of pixels away before the ranged attack takes place

    projectile_speed:
        the number of pixels per tick the projectile moves

    projectile_damage:
        the amount of damage a projectile does

    attack_period:
        the number of frames to wait before attacking again.
    """

    hp = 100
    speed = 3
    contact_damage = 3

    is_melee = False
    is_ranged = False

    clips = True
    activation_range = 0
    stationary = False

    attack_range = 256
    projectile_speed = 16
    projectile_damage = 3
    attack_period = 16

    def __init__(self):
        """
        create the class.

        Cooldown serves to prevent an enemy from firing
        or attacking every single tick. It increases by
        the attack_period every tick that it shoots,
        and then decreases by 1 every tick it doesn't shoot.
        It only shoots when the cooldown == 0.
        """
        super().__init__()

        self.image = pygame.Surface((48, 48))

        self.world = None

        self.current_hp = self.hp
        self.cooldown = 0

        self.rect = self.image.get_rect()

    def damage(self, amount):
        """
        Reduces the Enemy's health based on an event.

        :param amount: Int representing how much damage was taken
        """
        self.current_hp -= amount

    def ranged_attack(self, hero):
        """
        Fire a projectile towards the hero
        """
        pass

    def melee_attack(self, hero):
        """
        Attack the hero when approached.
        """
        pass

    def update(self, hero):
        """
        cause animation of the enemies.
        They move toward the position of the hero's center
        :param hero: The hero to move towards
        """
        if not self.stationary and self.get_dist() <= self.activation_range:
            if hero.rect.centerx > self.rect.centerx:
                self.movex(self.speed)
            if hero.rect.centery > self.rect.centery:
                self.movey(self.speed)
            if hero.rect.centerx < self.rect.centerx:
                self.movex(-self.speed)
            if hero.rect.centery < self.rect.centery:
                self.movey(-self.speed)

        if self.current_hp <= 0:
            self.kill()
            hero.increment_bomb_counter()

    def get_dist(self):
        """
        Return the distance from the enemy's center to the Hero's center.
        """
        dist = hypot(self.rect.centerx - c.CENTER[0], self.rect.centery - c.CENTER[1])

        return dist


class Turret(Enemy):
    """
    A stationary turret that fires projectiles at the player.
    """
    stationary = True
    is_ranged = True
    contact_damage = 0

    def __init__(self):
        super().__init__()

        self.image = h.load('badGuy.png')

    def ranged_attack(self, hero):
        """
        Fire a projectile towards the hero.
        :param hero: The target to track
        :returns proj: a Projectile entity with the correct speed.
        """
        changex = (hero.rect.centerx - self.rect.centerx)/self.projectile_speed
        changey = (hero.rect.centery - self.rect.centery)/self.projectile_speed

        proj = entities.Projectile(h.load('bullet.png'), self.rect.center, changex, changey, self.projectile_damage)

        self.cooldown += self.attack_period

        return proj


class Ghost(Enemy):
    """
    A moving ghost that can clip though walls and attacks the hero on contact
    """
    is_ranged = False
    contact_damage = 1
    activation_range = 1024
    Clips = False

    def __init__(self):
        super().__init__()

        self.image = h.load('ghost.png')