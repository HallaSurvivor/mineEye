"""
Exports the Heroes that the User can control as a list.

All Heroes subclass Hero, which in turn subclasses pygame Sprites.
"""
import os
import logging
from math import hypot
import pygame
from dependencies import pyganim
import entities
import helpers as h
from config import settings

module_logger = logging.getLogger('mineEye.hero')


class Hero(pygame.sprite.Sprite):
    """
    A class representing the Hero that the user controls.

    all of the base stats can be modified by items, and so are recreated as actual
    values inside of __init__()

    Thanks to those at programarcadegames.com for the basis of this code.
    """

    name = 'Hero'

    base_hp = 250
    base_speed = 10
    base_jump_height = 15
    base_double_jump_height = 0

    max_bombs = 3  # number of bombs in clip

    melee_damage_multiplier = 1
    ranged_damage_multiplier = 1

    melee_range_multiplier = 1

    base_bomb_refill_requirement = 4  # number of kills before being given another bomb

    can_doublejump = False
    take_falldamage = True

    multiple_weapon_drops = False
    weapon_pickup_range = 48

    melee_weapon = None
    ranged_weapon = None

    def __init__(self):
        """
        create the class, and create local variables based on the base variables that can be modified.
        """

        super().__init__()

        self.world = None

        self.logger = logging.getLogger('mineEye.hero.Hero')

        # Mutable variables that can change but may need to be reset
        self.hp = self.base_hp
        self.actual_speed = self.base_speed
        self.jump_height = self.base_jump_height
        self.double_jump_height = self.base_double_jump_height

        self.bombs = self.max_bombs
        self.bomb_refill_counter = 0
        self.bomb_refill_requirement = self.base_bomb_refill_requirement

        # Flags to help control motion
        self.start_jump = False
        self.start_double_jump = False

        self.jumping = False
        self.double_jumping = False
        self.jump_count = 0

        self.moving_left = False
        self.moving_right = False
        self.last_motion = 'right'

        # Sprite and PygAnim stuff
        self.animation_obj = {}
        self.conductor = None
        self.rect = pygame.Rect(0, 0, 48, 48)
        self.rect.center = (settings['WIDTH']/2, settings['HEIGHT']/2)

        self.create_animation_dict()

    def create_animation_dict(self):
        """
        Create an animation object and conductor to run the animations for walking, jumping, standing, etc.

        note: only right moving sprites exist. left sprites are simply reflections of the right sprites.

        Pulls all the images of a category in the Sprites/[hero name] folder
        Creates a Pyganim animation for each possible motion, then stores them in a dictionary
        Creates a Pyganim conductor to control the dictionary of animations

        Thanks to the pyganim example code for the basis of this code.
        """
        standing = [(os.path.join('Sprites', self.name, 'standing{num}.png'.format(num=num)), 0.1)
                    for num in range(3)]

        walking = [(os.path.join('Sprites', self.name, 'walking{num}.png'.format(num=num)), 0.1)
                   for num in range(8)]

        jumping = [(os.path.join('Sprites', self.name, 'jumping{num}.png'.format(num=num)), 0.1)
                   for num in range(4)]

        self.animation_obj['stand_right'] = pyganim.PygAnimation(standing)

        self.animation_obj['stand_left'] = self.animation_obj['stand_right'].getCopy()
        self.animation_obj['stand_left'].flip(True, False)
        self.animation_obj['stand_left'].makeTransformsPermanent()

        self.animation_obj['move_right'] = pyganim.PygAnimation(walking)

        self.animation_obj['move_left'] = self.animation_obj['move_right'].getCopy()
        self.animation_obj['move_left'].flip(True, False)
        self.animation_obj['move_left'].makeTransformsPermanent()

        self.animation_obj['jump_right'] = pyganim.PygAnimation(jumping)

        self.animation_obj['jump_left'] = self.animation_obj['jump_right'].getCopy()
        self.animation_obj['jump_left'].flip(True, False)
        self.animation_obj['jump_left'].makeTransformsPermanent()

        self.conductor = pyganim.PygConductor(self.animation_obj)

    def draw(self, screen):
        """
        Draw the animated Hero to the screen in a certain way based on user input
        :param screen: The screen on which to draw
        """
        if self.jump_count >= 4:
            self.jump_count = 0
            self.start_jump = False
            self.start_double_jump = False

        if self.start_jump or self.start_double_jump:
            self.jump_count += 1
            self.conductor.play()
            if self.last_motion == 'right':
                self.animation_obj['jump_right'].blit(screen, self.rect)

            elif self.last_motion == 'left':
                self.animation_obj['jump_left'].blit(screen, self.rect)

        elif self.moving_left or self.moving_right:
            self.conductor.play()
            if self.moving_left:
                self.animation_obj['move_left'].blit(screen, self.rect)

            elif self.moving_right:
                self.animation_obj['move_right'].blit(screen, self.rect)

        else:
            self.conductor.play()
            if self.last_motion == 'right':
                self.animation_obj['stand_right'].blit(screen, self.rect)

            elif self.last_motion == 'left':
                self.animation_obj['stand_left'].blit(screen, self.rect)

    def update(self):
        if settings['GOD MODE']:
            self.jump_height = 50

    def damage(self, amount):
        """
        Reduces the Hero's health based on an event.

        :param amount: Int representing how much damage was taken
        """
        if not settings['GOD MODE']:
            self.logger.info('Hero took {0} damage'.format(amount))
            self.hp -= amount
            self.logger.info('HP: {0}/{1}'.format(self.hp, self.base_hp))

    def drop_bomb(self):
        """
        Drop a bomb that destroys surrounding blocks and damages enemies.

        :returns bomb: A bomb entity
        """
        if not settings['GOD MODE']:
            self.bombs -= 1
        if self.last_motion == "right":
            x = 13
        elif self.last_motion == "left":
            x = -13
        else:
            x = 0
        bomb = entities.Bomb(h.load('bomb.png'), self.rect.center, x, -20)
        return bomb

    def reset_all(self):
        """
        Resets all mutable variables to the hero's baseline.
        """
        self.hp = self.base_hp
        self.actual_damage_multiplier = self.base_damage_multiplier
        self.actual_speed = self.base_speed
        self.jump_height = self.base_jump_height
        self.double_jump_height = self.base_double_jump_height
        self.take_falldamage = self.can_take_falldamage
        self.bombs = self.base_bomb_count

    def change_speed(self, amount):
        """
        Change self.actual_speed
        :param amount: A multiplier to change the speed.
        """
        self.actual_speed = amount*self.base_speed

    def change_jump_height(self, amount):
        """
        Change actual self.jump_height
        :param amount: A multiplier to change jump height
        """
        self.jump_height = amount*self.base_jump_height

    def change_double_jump_height(self, amount):
        """
        Change the double jump height
        :param amount: A multiplier to change doublejump height
        """
        self.double_jump_height = amount*self.base_double_jump_height

    def increment_bomb_counter(self):
        """
        Add 1 to the bomb counter, recover a bomb if the counter fills
        """
        self.bomb_refill_counter += 1
        if self.bomb_refill_counter >= self.bomb_refill_requirement:
            self.bomb_refill_counter = 0
            self.recover_bomb()

    def recover_bomb(self):
        """
        If the bombs are not full, add another bomb.
        """
        if self.bombs < self.max_bombs:
            self.bombs += 1

    def get_nearest_node(self):
        """
        Change hero.nearest_node to be the node closest to the hero's center.
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

        self.logger.debug('Nearest node to hero: {node}'.format(node=nearest_node))
        return nearest_node