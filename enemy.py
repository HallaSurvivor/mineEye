"""
Exports the Enemy class that the User actually controls.
"""
import pygame
import helpers as h
import entities


class Enemy(pygame.sprite.Sprite):
    """
    An Enemy superclass meant to be subclassed by individual enemies.

    contact_damage - the amount of damage the enemy does when the player touches it.

    attack_range - the number of pixels away before the ranged attack takes place

    projectile_speed - the number of pixels per tick the projectile moves

    attack_period - the number of frames to wait before attacking again.
    """

    hp = 100
    speed = 3
    contact_damage = 3

    is_melee = False
    is_ranged = False

    stationary = False

    attack_range = 256
    projectile_speed = 16
    projectile_damage = 3
    attack_period = 16


    def __init__(self):
        """
        create the class.
        note damage_player_on_touch means that when the player is hitting the bad guy damage is done. This would be true of a bwarler type chractor
        """
        super().__init__()

        self.image = pygame.Surface((48, 48))

        self.world = None

        self.current_hp = self.hp

        self.melee_attack_cooldown = 0

        self.ranged_attack_cooldown = 0

        self.damage_player_on_touch = True

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

    def update(self, hero):
        """
        cause animation of the enemies.
        They move toward the positon of the hero's center
        :param hero: The hero to move towards
        """
        if not self.stationary:
            if hero.rect.centerx > self.rect.centerx:
                self.movex(4)
            if hero.rect.centery > self.rect.centery:
                self.movey(4)
            if hero.rect.centerx < self.rect.centerx:
                self.movex(-4)
            if hero.rect.centery < self.rect.centery:
                self.movey(-4)
            if hero.rect.center is self.rect.center:
                self.rect.y = 0
                self.rect.x = 0



class Turret(Enemy):
    """
    A stationary turret that fires projectiles at the player.
    """

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

        self.ranged_attack_cooldown += self.attack_period

        return proj