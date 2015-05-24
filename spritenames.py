"""
Defines the load(imagename) function to import sprites into the game

Defines the create_background(background_tile) function to create a tiled background
"""
import os
import pygame
import config

_image_library = {}

def load(imagename):
    """
    Retrieves previously loaded images from _image_library, and stores newly created ones there as they are called.

    :param imagename: a string representing the name of the image to load, including extension
    :returns image: a pygame surface created from the file at imagename

    thanks to Blake at NerdParadise for the basis of this code.
    """
    global _image_library
    image = _image_library.get(imagename)

    if image is None:
        image = pygame.image.load(os.path.join("Sprites", imagename))
        _image_library[imagename] = image

    return image


def create_background(background_tile):
    """
    Creates a surface made by tiling the background_tile image

    TODO: store it in _image_library for future use

    :param background_tile: a pygame surface that can be tiled
    :returns background: a pygame surface consisting of the tiled background_tile
    """

    background = pygame.Surface(config.SCREEN_RESOLUTION)
    for i in range(0, config.SCREEN_RESOLUTION[0], background_tile.get_width()):
        for n in range(0, config.SCREEN_RESOLUTION[1], background_tile.get_height()):
            background.blit(background_tile, (i, n))

    return background


class Hero(pygame.sprite.Sprite):
    """
    The Hero that the player controls

    TODO: Add multiple hero options

    self.image is the picture associated with the Hero, should be 48x48

    self.change_x is the Hero's movement speed in the x direction
    self.change_y is the Hero's movement speed in the y direction

    self.rect is the Hero's bounding box
        .rect.y is the box's top left corner's y position
        .rect.x is the box's top left corner's x position

    self.walls is the list of walls the Hero can collide with

    Thanks to those at programarcadegames.com for the basis of this code.
    """
    def __init__(self):
        """
        create the class.
        """
        super().__init__()

        self.image = load('herosprite.png')

        self.change_x = 0
        self.change_y = 0

        self.rect = self.image.get_rect()

        self.rect.x = 0
        self.rect.y = 0

        self.walls = None

    def changespeed(self, x, y):
        """
        Changes the Hero's movement speed
        :param x: int representing the change in x speed
        :param y: int representing the change in y speed
        """
        self.change_x += x
        self.change_y += y

    def update(self):
        """
        Update the Hero's position and check for any collisions
        """

        self.rect.x += self.change_x

        block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            else:
                self.rect.left = block.rect.right

        self.rect.y += self.change_y

        block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            else:
                self.rect.top = block.rect.bottom


class Wall(pygame.sprite.Sprite):
    """
    Wall the Hero can collide with.
    """
    def __init__(self, x, y, image):
        """
        Create the wall and its location
        :param x: Int representing the x position of the wall's top left corner
        :param y: Int representing the y position of the wall's top left corner
        :param image: a pygame surface associated with the wall's texture
        """
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x