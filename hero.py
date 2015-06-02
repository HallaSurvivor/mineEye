"""
Exports the Hero class that the User actually controls.
"""
import pygame
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
    base_double_jump_height = 15

    can_doublejump = False

    def __init__(self):
        """
        create the class.
        """
        super().__init__()

        self.image = pygame.Surface((48, 48))

        self.world = None

        self.hp = self.base_hp
        self.actual_speed = self.base_speed
        self.jump_height = self.base_jump_height
        self.double_jump_height = self.base_double_jump_height

        self.jumping = False
        self.double_jumping = False
        self.moving_left = False
        self.moving_right = False

        self.run_timer = True

        self.rect = self.image.get_rect()
        self.rect.center = constants.CENTER

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


class Hero1(Hero):
    """
    A hero with double jump abilities.
    """

    name = "Hero 1"
    description = "A hero with double jump abilities"

    can_doublejump = True

    def __init__(self):
        super().__init__()

        self.image = h.load('herosprite.png')
        self.reset_all()


class Hero2(Hero):
    """
    A fast hero with low health.
    """

    name = "Hero 2"
    description = "A fast hero with low health"

    base_hp = 250
    base_speed = 10
    base_jump_height = 15

    def __init__(self):
        super().__init__()

        self.image = h.load('herosprite2.png')

        self.reset_all()


class Hero3(Hero):
    """
    Just a regular hero.
    """

    name = "Hero 3"
    description = "Nothing fancy. Just a regular hero."

    def __init__(self):
        super().__init__()

        self.image = h.load('herosprite3.png')

        self.reset_all()


hero_list = [Hero1, Hero2, Hero3]