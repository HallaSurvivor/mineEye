"""
Exports a variety of helper functions to cut down on repetitive code.
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


def blit_text(text, screen, position):
    """
    Automatically blit text to a certain position on the screen.
    :param text: the pygame text to be blitted
    :param screen: the screen to blit to
    :param position: the vertical position to blit to
    :returns rect: the rect to which the text is blitted
    """

    rect = text.get_rect()
    rect.centerx = constants.CENTER[0]
    rect.centery = .125*position*config.SCREEN_RESOLUTION[1]
    screen.blit(text, rect)

    return rect