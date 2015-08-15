"""
Exports the Enemy classes that the Hero has to battle.
"""
import os
import logging
from math import hypot, sin, cos, tan, atan, pi
import pygame
from dependencies import pyganim
import helpers as h
from config import settings
import constants
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

    name = ''
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

    death_sound = None

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

        self.world = world

        self.graph = self.world.nodes

        self.yspeed = 0  # separate y speed for gravity

        self.current_hp = self.hp
        self.cooldown = 0

        self.rect = pygame.Rect(0, 0, 64, 64)

        self.pathfind_timer = 0
        self.path = None

        self.animation_obj = {}
        self.conductor = None

        self.create_animation_dict()

    def __repr__(self):
        return '{enemy} at position: {pos}'.format(enemy=type(self).__name__, pos=self.rect.center)

    def damage(self, amount):
        """
        Reduces the Enemy's health based on an event.

        :param amount: Int representing how much damage was taken
        """
        self.logger.info('{enemy} damaged by {amount}'.format(enemy=self, amount=amount))
        self.current_hp -= amount

    def create_animation_dict(self):
        """
        Create the animation object and the conductor to run the animations.

        For more details, see the hero.create_animation_dict()

        Thanks to the pyganim example code for the basis of thsi code
        """

        self.logger.debug('Creating animation dict for {0}'.format(self))

        movement = [(os.path.join('Sprites', self.name, '{num}.png'.format(num=num)), 0.1)
                    for num in range(2)]

        self.animation_obj['move_right'] = pyganim.PygAnimation(movement)
        self.animation_obj['move_right'].convert()
        self.animation_obj['move_right'].set_colorkey(constants.COLORKEY)

        self.animation_obj['move_left'] = self.animation_obj['move_right'].getCopy()
        self.animation_obj['move_left'].flip(True, False)
        self.animation_obj['move_left'].makeTransformsPermanent()

        self.conductor = pyganim.PygConductor(self.animation_obj)

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

    def a_star(self, hero, n=7):
        """
        Calculate the A* algorithm to pathfind towards the hero.

        Thanks to redblobgames.com for the basis of this code!
        """
        frontier = h.Queue()
        came_from = {}
        cost_so_far = {}

        start = self.get_nearest_node()
        goal = hero.get_nearest_node()

        frontier.put(start, 0)

        came_from[start] = None
        cost_so_far[start] = 0
        while not frontier.is_empty() and n > 0:
            current = frontier.get()

            if current == goal:
                break

            for next_node in self.graph.get_neighbors(current):
                new_cost = cost_so_far[current] + self.graph.cost(current, next_node)
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.graph.heuristic(goal, next_node)
                    frontier.put(next_node, priority)
                    came_from[next_node] = current

            n -= 1

        return came_from, current

    def reconstruct_path(self, came_from, goal):
        start = self.get_nearest_node()

        current = goal
        path = [current]
        while current != start:
            try:
                current = came_from[current]
                path.append(current)
            except KeyError:
                # self.logger.exception('Key error in reconstruct path, node {0}'.format(current))
                pass
        path.reverse()
        return [self.graph.nodes.index(node) for node in path]

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

    def check_x_collisions(self):
        """
        Prevent the enemy from moving through walls.

        Check for collisions, then adjust the enemy position if it collides with anything
        """
        block_hit_list = pygame.sprite.spritecollide(self, self.world.block_list, False)
        for block in block_hit_list:
            if self.rect.x < block.rect.x:
                self.rect.right = block.rect.left
            elif self.rect.x > block.rect.x:
                self.rect.left = block.rect.right

    def check_y_collisions(self):
        """
        Prevent the enemy from moving through walls.

        Check for collisions, then adjust the enemy position if it collides with anything
        """
        block_hit_list = pygame.sprite.spritecollide(self, self.world.block_list, False)
        for block in block_hit_list:
            if self.rect.y < block.rect.y:
                self.rect.bottom = block.rect.top
            elif self.rect.y > block.rect.y:
                self.rect.top = block.rect.bottom

    def straight_to_hero(self, hero):
        """
        Move directly towards the hero, regardless of walls

        Used by enemies that don't clip, such as ghosts
        :param hero: The hero to move towards
        """
        if hero.rect.centerx > self.rect.centerx:
            self.movex(self.speed)
        if hero.rect.centery > self.rect.centery:
            self.movey(self.speed)
        if hero.rect.centerx < self.rect.centerx:
            self.movex(-self.speed)
        if hero.rect.centery < self.rect.centery:
            self.movey(-self.speed)

    def pathfind(self, hero):
        """
        Use A* pathfinding to move efficiently towards the hero

        Importantly, the nodes change alongside the motion of the room,
        Because of this, the nodes manipulated here are references to the
        nodes stored inside of World.nodes.nodes. This makes it possible to
        move those nodes' positions, and have the pathfinding here update
        automatically.

        :param hero: The hero to use as a goal
        """
        self.logger.debug('{0} started pathfinding'.format(self))
        if self.pathfind_timer == 0:
            came_from, current = self.a_star(hero)
            self.path = self.reconstruct_path(came_from, current)
            self.pathfind_timer += 16
        else:
            self.pathfind_timer -= 1

        try:
            if self.graph.nodes[self.path[0]] == self.rect.center:
                self.logger.debug('{0} reached node {1}'.format(self, self.rect.center))
                self.path.pop(0)
        except IndexError:
            self.logger.debug('{enemy} ran out of nodes in path'.format(enemy=self))

        if len(self.path) > 0:
            node_index = self.path[0]
            node = self.graph.nodes[node_index]

            if node[0] > self.rect.centerx:
                self.movex(self.speed)

            elif node[0] < self.rect.centerx:
                self.movex(-self.speed)

            if node[1] > self.rect.centery:
                self.movey(self.speed)

            elif node[1] < self.rect.centery:
                self.movey(-self.speed)

    def get_dist_from_hero(self):
        """
        Return the distance from the enemy's center to the Hero's center
        """
        return hypot(self.rect.centerx - settings['HEIGHT']/2, self.rect.centery - settings['WIDTH']/2)

    def get_normalized_vec_to_hero(self):
        """
        Return a unit vector pointing in the direction of the Hero's Center
        """

        norm_factor = self.get_dist_from_hero()

        changex = (settings['WIDTH']/2 - self.rect.centerx)/norm_factor
        changey = (settings['HEIGHT']/2 - self.rect.centery)/norm_factor

        return changex, changey

    def get_theta(self, changex, changey):
        """
        Return the angle of a vector

        :param changex: X component of the vector
        :param changey: Y component of the vector
        :return: Theta
        """

        try:
            return atan(changey/changex)
        except ZeroDivisionError:
            if changey >= 0:
                return pi
            else:
                return -pi

    def change_angle(self, changex0, changey0, delta_theta):
        """
        Return a unit vector corresponding to rotating  (changex0, changey0) by delta_theta

        :param delta_theta: Change in theta in radians
        """

        theta0 = self.get_theta(changex0, changey0)

        theta = theta0 + delta_theta

        x = cos(theta)
        y = sin(theta)

        return x, y

    def get_nearest_node(self):
        """
        Return the node nearest to the Enemy's center.
        """

        nearest_node = None
        for node in self.world.nodes.nodes:
            if hypot(node[0] - settings['WIDTH']/2, node[1] - settings['HEIGHT']) <= 1200:
                if nearest_node is None:
                    nearest_node = node
                    current_dist = hypot(self.rect.centerx - node[0], self.rect.centery - node[1])
                else:
                    new_dist = hypot(self.rect.centerx - node[0], self.rect.centery - node[1])
                    if new_dist < current_dist:
                        nearest_node = node
                        current_dist = new_dist

        self.logger.debug('Nearest node to {enemy}: {node}'.format(enemy=self, node=nearest_node))
        return nearest_node

    def update(self, hero):
        """
        Cause enemy movement/death.

        If the enemy moves and doesn't clip (ghosts):
            They move toward the position of the hero's center

        If the enemy moves and DOES clip:
            Call the Hero's position a "goal" and use A* pathfinding

        :param hero: The hero to move towards
        """
        if not self.stationary and self.get_dist_from_hero() <= self.activation_range:
            if not self.flying:
                self.calc_gravity()

            if self.clips:
                self.pathfind(hero)
            else:
                self.straight_to_hero(hero)

        if self.current_hp <= 0:
            self.kill()
            if settings['PLAY_SFX']:
                try:
                    self.death_sound.play()
                except AttributeError:
                    pass

            hero.increment_bomb_counter()

            if hero.speed_boost_on_kill:
                hero.actual_speed += 2
                hero.speed_boost_counter = 1

    def draw(self, screen):
        """
        Draw the animated enemy to the screen

        :param screen: The screen to draw to
        """

        hero_x = settings['SCREEN_RESOLUTION'][0]/2

        self.conductor.play()
        if self.rect.centerx >= hero_x:
            self.animation_obj['move_left'].blit(screen, self.rect)
        else:
            self.animation_obj['move_right'].blit(screen, self.rect)


class Turret(Enemy):
    """
    A stationary turret that fires projectiles at the player.
    """
    stationary = True
    is_ranged = True
    contact_damage = 0
    attack_period = 16
    name = 'Turret'

    def __init__(self, *args):
        super().__init__(*args)

    def ranged_attack(self, hero):
        """
        Fire a list of projectiles towards the hero.

        :param hero: The target to track
        :returns proj: a Projectile entity with the correct speed.
        """

        changex, changey = self.get_normalized_vec_to_hero()
        changex2, changey2 = self.change_angle(abs(changex), abs(changey), pi/6)
        changex3, changey3 = self.change_angle(abs(changex), abs(changey), -pi/6)

        changex *= self.projectile_speed
        changey *= self.projectile_speed

        changex2 *= self.projectile_speed/2
        changey2 *= self.projectile_speed/2

        changex3 *= self.projectile_speed/2
        changey3 *= self.projectile_speed/2

        if settings['WIDTH']/2 < self.rect.centerx:
            changex2 *= -1
            changex3 *= -1

        if settings['HEIGHT']/2 < self.rect.centery:
            changey2 *= -1
            changey3 *= -1

        proj = entities.Projectile(h.load('bullet.png'), self.rect.center, changex, changey,
                                   self.projectile_damage, self)

        proj2 = entities.Projectile(h.load('bullet.png'), self.rect.center, changex2, changey2,
                                    self.projectile_damage, self)

        proj3 = entities.Projectile(h.load('bullet.png'), self.rect.center, changex3, changey3,
                                    self.projectile_damage, self)

        self.cooldown += self.attack_period

        if self.world.region:
            return [proj, proj2, proj3]

        else:
            return [proj]


class Ghost(Enemy):
    """
    A moving ghost that can clip though walls and attacks the hero on contact
    """
    contact_damage = 1
    activation_range = 1024
    clips = False
    flying = True
    name = 'Ghost'

    def __init__(self, *args):
        super().__init__(*args)


class FireBat(Enemy):
    activation_range = 600
    speed = 4
    contact_damage = 4
    flying = True
    name = 'FireBat'

    death_sound = h.load_sound('firebat.wav')

    def __init__(self, *args):
        super().__init__(*args)
