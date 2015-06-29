"""
Exports the Enemy classes that the Hero has to battle.
"""
import logging
from math import hypot
import pygame
import helpers as h
from config import settings
import entities

module_logger = logging.getLogger('mineEye.enemy')


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
    flying = False

    attack_range = 256
    projectile_speed = 16
    projectile_damage = 3
    attack_period = 16

    def __init__(self, world):
        """
        create the class.

        Cooldown serves to prevent an enemy from firing
        or attacking every single tick. It increases by
        the attack_period every tick that it shoots,
        and then decreases by 1 every tick it doesn't shoot.
        It only shoots when the cooldown == 0.
        """
        super().__init__()

        self.logger = logging.getLogger('mineEye.enemy.Enemy')

        self.image = pygame.Surface((48, 48))

        self.world = world

        self.yspeed = 0  # separate y speed for gravity

        self.current_hp = self.hp
        self.cooldown = 0

        self.rect = self.image.get_rect()

        self.previous_location = self.rect.center

    def __repr__(self):
        return '{enemy} at position: {pos}'.format(enemy=type(self).__name__, pos=self.rect.center)

    def damage(self, amount):
        """
        Reduces the Enemy's health based on an event.

        :param amount: Int representing how much damage was taken
        """
        self.logger.info('{enemy} damaged by {amount}'.format(enemy=self, amount=amount))
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

    def a_star(self, hero):
        """
        Calculate the A* algorithm to pathfind towards the hero.

        Thanks to redblobgames.com for the basis of this code!
        """
        frontier = h.Queue()
        came_from = {}
        cost_so_far = {}

        graph = self.world.nodes
        start = self.get_nearest_node()
        goal = hero.get_nearest_node()

        frontier.put(start, 0)

        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.is_empty():
            current = frontier.get()

            if current == goal:
                break

            for next_node in graph.get_neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next_node)
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + graph.heuristic(goal, next_node)
                    frontier.put(next_node, priority)
                    came_from[next_node] = current

        return came_from

    def reconstruct_path(self, hero, came_from):
        start = self.get_nearest_node()
        goal = hero.get_nearest_node()

        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()

        return path

    def calc_gravity(self):
        self.yspeed -= self.world.gravity_acceleration
        self.logger.debug('{enemy} yspeed: {value}'.format(enemy=self, value=self.yspeed))
        self.movey(self.yspeed)

        block_hit_list = pygame.sprite.spritecollide(self, self.world.block_list, False)
        for block in block_hit_list:

            if self.yspeed < 0:
                self.rect.top = block.rect.bottom
                self.yspeed = 0
            elif self.yspeed > 0:
                self.rect.bottom = block.rect.top
                self.yspeed = 0

    def basic_pathfinding(self, hero):
        """
        A basic pathfinding alg to replace the buggy A* implementation for ground-only enemies

        :param hero: The hero to compare against
        """
        if not self.flying:
            self.calc_gravity()

        if abs(hero.rect.centerx - self.rect.centerx) < 8:
            direction = 'none'

        elif hero.rect.centerx > self.rect.centerx:
            self.movex(self.speed)
            direction = 'right'

        elif hero.rect.centerx < self.rect.centerx:
            self.movex(-self.speed)
            direction = 'left'

        block_hit_list = pygame.sprite.spritecollide(self, self.world.block_list, False)
        for block in block_hit_list:
            if direction == 'right':
                self.rect.right = block.rect.left
                # self.logger.debug("{enemy} hit a block from the left".format(enemy=self))
            elif direction == 'left':
                self.rect.left = block.rect.right
                # self.logger.debug("{enemy} hit a block from the right".format(enemy=self))
            else:
                self.logger.error("{0} moving, but it hit something... ya done messed up".format(self))

            if self.rect.bottom >= hero.rect.bottom:
                self.yspeed = -self.speed

    def update(self, hero):
        """
        Cause enemy movement/death.

        If the enemy moves and doesn't clip (ghosts):
            They move toward the position of the hero's center

        If the enemy moves and DOES clip:
            (Call the Hero's position a "goal" and use A* pathfinding)
                depreciated due to bugs. Might reimplement later

            Use the basic_pathfinding method to move generally towards the hero.

        :param hero: The hero to move towards
        """
        if not self.stationary and self.get_dist() <= self.activation_range:
            if not self.clips:
                if hero.rect.centerx > self.rect.centerx:
                    self.movex(self.speed)
                if hero.rect.centery > self.rect.centery:
                    self.movey(self.speed)
                if hero.rect.centerx < self.rect.centerx:
                    self.movex(-self.speed)
                if hero.rect.centery < self.rect.centery:
                    self.movey(-self.speed)
            else:
                if not self.flying:
                    self.basic_pathfinding(hero)
                else:
                    path = self.reconstruct_path(hero, self.a_star(hero))
                    if path[0] == self.get_nearest_node():
                        path.pop(0)

                    if len(path) > 0:
                        if path[0][0] > self.rect.centerx:
                            self.movex(self.speed)
                        if path[0][1] > self.rect.centery:
                            self.movey(self.speed)
                        if path[0][0] < self.rect.centerx:
                            self.movex(-self.speed)
                        if path[0][1] < self.rect.centery:
                            self.movey(-self.speed)

        if self.current_hp <= 0:
            self.kill()
            hero.increment_bomb_counter()

    def get_dist(self, node=None):
        """
        Return the distance from the enemy's center to the Hero's center or a node
        """
        if node is None:
            dist = hypot(self.rect.centerx - settings['HEIGHT']/2, self.rect.centery - settings['WIDTH']/2)

        else:
            dist = hypot(self.rect.centerx - node[0], self.rect.centery - node[1])

        return dist

    def get_nearest_node(self):
        nearest_node = None
        for node in self.world.nodes.nodes:
            if nearest_node is None:
                nearest_node = node
                current_dist = self.get_dist(node)
            else:
                new_dist = self.get_dist(node)
                if new_dist < current_dist:
                    nearest_node = node
                    current_dist = new_dist

        return nearest_node


class Turret(Enemy):
    """
    A stationary turret that fires projectiles at the player.
    """
    stationary = True
    is_ranged = True
    contact_damage = 0

    def __init__(self, *args):
        super().__init__(*args)

        self.image = h.load('badGuy.png')

    def ranged_attack(self, hero):
        """
        Fire a projectile towards the hero.
        :param hero: The target to track
        :returns proj: a Projectile entity with the correct speed.
        """
        changex = (hero.rect.centerx - self.rect.centerx)/self.projectile_speed
        changey = (hero.rect.centery - self.rect.centery)/self.projectile_speed

        proj = entities.Projectile(h.load('bullet.png'), self.rect.center, changex, changey, self.projectile_damage, self)

        self.cooldown += self.attack_period

        return proj


class Ghost(Enemy):
    """
    A moving ghost that can clip though walls and attacks the hero on contact
    """
    contact_damage = 1
    activation_range = 1024
    clips = False
    flying = True

    def __init__(self, *args):
        super().__init__(*args)

        self.image = h.load('ghost.png')


class FireBat(Enemy):
    activation_range = 1024
    speed = 5

    def __init__(self, *args):
        super().__init__(*args)

        self.image = h.load('firebat.png')
