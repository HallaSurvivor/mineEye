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
    A superclass to be inherited by all the possible Heroes that the user can control.

    all of the base stats can be modified by items, and so are recreated as actual
    values inside of __init__()

    name:
        the name of the hero to be displayed on screen during hero selection

    description:
        a description of the hero to be displayed during hero selection

    base_hp:
        the base health of the hero

    base_damage_multiplier:
        the amount by which to multiply a weapon's power when used

    base_speed:
        the base left/right speed of the hero

    base_jump_height:
        the base upward speed of the hero

    base_double_jump_height:
        the base upward speed for the second jump for those heroes who can

    base_bomb_refill_requirement:
        the base value for how many enemies need to be killed before
        the hero recovers a bomb

    self.image:
        the pygame Sprite associated with the Hero, should be 48x48

    self.world:
        the world in which the hero is placed

    self.hp:
        the current health of the hero

    self.can_doublejump:
        True if the hero can doublejump.
        False by default

    self.can_take_falldamage:
        False if the hero never takes fall damage.
        True by default

    self.rect:
        the Hero's bounding box
        .rect.y is the box's top left corner's y position
        .rect.x is the box's top left corner's x position

    Thanks to those at programarcadegames.com for the basis of this code.
    """

    name = ""
    description = ""

    base_hp = 500
    base_damage_multiplier = 1
    base_speed = 7
    base_jump_height = 12
    base_double_jump_height = 0
    base_bomb_refill_requirement = 4

    can_doublejump = False

    can_take_falldamage = True

    bomb_control = False
    base_bomb_count = 3

    multiple_weapon_drops = False
    weapon_pickup_range = 192

    melee_weapon = None
    ranged_weapon = None

    def __init__(self):
        """
        create the class, and create local variables based on the base variables that can be modified.
        """
        super().__init__()

        self.world = None

        self.logger = logging.getLogger('mineEye.hero.Hero')

        # Mutable variables that items, etc. can change
        self.hp = self.base_hp
        self.actual_damage_multiplier = self.base_damage_multiplier
        self.actual_speed = self.base_speed
        self.jump_height = self.base_jump_height
        self.double_jump_height = self.base_double_jump_height
        self.take_falldamage = self.can_take_falldamage

        self.max_bombs = self.base_bomb_count
        self.bombs = self.base_bomb_count
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

        # A timer variable to control when it's running
        self.run_timer = True

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


class Demo(Hero):
    """
    A demolition expert with control over bombs.
    """

    name = "Demo"
    description = "A demolition expert with control over bombs."

    bomb_control = True
    base_bomb_count = 5

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger('mineEye.hero.Demo')
        self.reset_all()


class Jumpy(Hero):
    """
    A hero with double jump abilities. Doesn't take fall damage
    """

    name = "Jumpy"
    description = "A hero with double jump abilities. Doesn't take fall damage"

    base_jump_height = 15
    base_double_jump_height = 15

    can_doublejump = True
    can_take_falldamage = False

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger('mineEye.hero.Jumpy')
        self.reset_all()


class Speedy(Hero):
    """
    A fast hero with low health.
    """

    name = "Speedy"
    description = "A fast hero with low health"

    base_hp = 250
    base_speed = 10
    base_jump_height = 15

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger('mineEye.hero.Speedy')
        self.reset_all()


hero_list = [Demo, Jumpy, Speedy]