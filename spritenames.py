"""
Defines the load(imagename) function to import sprites into the game

Defines the create_background(background_tile) function to create a tiled background

Defines the Hero class to represent the hero (player)

Defines the Wall class to represent a tile the Hero cannot move through
"""
import os
import pygame
import config
import constants

_image_library = {}
_font_library = {}


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
        try:
            image = pygame.image.load(os.path.join("Sprites", imagename))
            _image_library[imagename] = image
        except:
            raise FileNotFoundError

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


def load_font(fontname, size):
    """
    Loads a font if it doesn't already exist, retrieves it from a dictionary if it does.
    :param fontname: a string representing the name of the font to load, including extension
    :param size: an int representing the size to make the loaded font
    :returns font: a pygame font created from the font at fontname
    """
    global _font_library
    font = _font_library.get((fontname, size))

    if font is None:
        try:
            font = pygame.font.Font(os.path.join('Fonts', fontname), size)
            _font_library[(fontname, size)] = font
        except:
            raise FileNotFoundError

    return font


def play_music(musicname):
    """
    Load a pygame music object from a music file and play it if config.PLAY_MUSIC is True.
    :param musicname: The name of the music file to be loaded and played, including extension.
        must be located in /Music
    """
    try:
        pygame.mixer.music.stop()  # Stop any previously playing music
        pygame.mixer.music.load(os.path.join('Music', musicname))
        pygame.mixer.music.play()
    except:
        raise FileNotFoundError


class Hero(pygame.sprite.Sprite):
    """
    The Hero that the player controls

    TODO: Add multiple hero options

    self.image is the picture associated with the Hero, should be 48x48

    self.hp is the Health remaining for the Hero.

    self.change_x is the Hero's movement speed in the x direction
    self.change_y is the Hero's movement speed in the y direction

    self.rect is the Hero's bounding box
        .rect.y is the box's top left corner's y position
        .rect.x is the box's top left corner's x position

    Thanks to those at programarcadegames.com for the basis of this code.
    """
    def __init__(self):
        """
        create the class.
        """
        super().__init__()

        self.image = load('herosprite.png')

        self.hp = 5000

        self.change_x = 0
        self.change_y = 0

        self.rect = self.image.get_rect()
        self.rect.center = constants.CENTER

    def damage(self, amount):
        """
        Reduces the Hero's health based on an event.
        :param amount: Int representing how much damage was taken
        """
        self.hp -= amount


class Wall(pygame.sprite.Sprite):
    """
    Wall the Hero can collide with.

    self.damage_player is True if the player is hurt on contact (spikes) but False otherwise
    """
    def __init__(self, x, y, image, damage_player=False):
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

        self.damage_player = damage_player

    def update(self):
        """
        Update the blocks.
        """
        pass

    def movex(self, xspeed):
        """
        Move the wall in the X direction.
        Collisions are handled in the Room class, since the entire room
            needs to stop moving when a single Wall collides with the hero.
        Movement is split between X and Y so that collision checking only has to deal with
            one at a time.

        :param xpseed: Int representing the change in x direction
        """

        self.rect.x += xspeed

    def movey(self, yspeed):
        """
        Move the wall in the Y direction.
        Collisions are handled in the Room class, since the entire room
            needs to stop moving when a single Wall collides with the hero.
        Movement is split between X and Y so that collision checking only has to deal with
            one at a time.

        :param yspeed:  Inte representing the change in y direction
        """

        self.rect.y += yspeed