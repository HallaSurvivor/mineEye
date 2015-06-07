"""
Exports the Hero class that the User actually controls.
"""
import os
import pygame
import pyganim
import constants
import helpers as h


class Hero(pygame.sprite.Sprite):
    """
    A superclass to be inherited by all the possible Heroes that the user can control.

    name is the name of the hero to be displayed on screen during hero selection

    description is a description of the hero to be displayed during hero selection

    base_hp is the base health of the heroes

    base_speed is the base speed of the heroes

    base_jump_height is the base jump height of the heroes

    base_double_jump_height is the base height of the second jump for those heroes who can

    self.image is the picture associated with the Hero, should be 48x48

    self.world is the world in which the hero is placed

    self.hp is the current health of the hero

    self.can_doublejump is True if the hero can doublejump. False by default

    self.can_take_falldamage is False if the hero never takes fall damage. True by default

    self.rect is the Hero's bounding box
        .rect.y is the box's top left corner's y position
        .rect.x is the box's top left corner's x position

    Thanks to those at programarcadegames.com for the basis of this code.
    """

    name = ""
    description = ""

    base_hp = 500
    base_speed = 7
    base_jump_height = 12
    base_double_jump_height = 0

    can_doublejump = False

    can_take_falldamage = True

    def __init__(self):
        """
        create the class.
        """
        super().__init__()

        self.world = None

        self.hp = self.base_hp
        self.actual_speed = self.base_speed
        self.jump_height = self.base_jump_height
        self.double_jump_height = self.base_double_jump_height
        self.take_falldamage = self.can_take_falldamage

        self.start_jump = False
        self.start_double_jump = False

        self.jumping = False
        self.double_jumping = False
        self.jump_count = 0

        self.moving_left = False
        self.moving_right = False
        self.last_motion = 'right'

        self.run_timer = True

        self.animation_obj = {}
        self.conductor = None
        self.rect = pygame.Rect(0, 0, 48, 48)
        self.rect.center = constants.CENTER

    def create_animation_dict(self):
        """
        Create an animation object and conductor to run the animations for walking, jumping, standing, etc.

        note: only right moving sprites exist. left sprites are simply reflections of the right sprites.

        Pulls all the images of a category in the Sprites/[hero name] folder
        Creates a Pyganim animation for each possible motion, then stores them in a dictionary
        Creates a Pyganim conductor to control the dictionary of animations

        Thanks to the pyganim example code for the basis of this code.
        """
        standing = [(os.path.join('Sprites', self.name, 'standing{num}.png'.format(num=num)), 0.1) for num in range(3)]
        walking = [(os.path.join('Sprites', self.name, 'walking{num}.png'.format(num=num)), 0.1) for num in range(8)]
        jumping = [(os.path.join('Sprites', self.name, 'jumping{num}.png'.format(num=num)), 0.1) for num in range(4)]

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

    def damage(self, amount):
        """
        Reduces the Hero's health based on an event.
        :param amount: Int representing how much damage was taken
        """
        self.hp -= amount

    def reset_all(self):
        """
        Resets the speed, jump_height, and double_jump_height to the hero's baseline.
        """
        self.hp = self.base_hp
        self.actual_speed = self.base_speed
        self.jump_height = self.base_jump_height
        self.double_jump_height = self.base_double_jump_height
        self.take_falldamage = self.can_take_falldamage

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


class Normal(Hero):
    """
    Just a regular hero.
    """

    name = "Normal"
    description = "Nothing fancy. Just a regular hero."

    def __init__(self):
        super().__init__()
        self.create_animation_dict()
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
        self.create_animation_dict()
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
        self.create_animation_dict()
        self.reset_all()


hero_list = [Normal, Jumpy, Speedy]