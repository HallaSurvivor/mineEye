"""
Exports a variety of helper functions to cut down on repetitive code.
"""
import os
import collections
import pygame
from config import settings
import constants as c

# Caches for sprites and fonts to mitigate the slow loading process
_image_library = {}
_font_library = {}


class Sprite(pygame.sprite.Sprite):
    """
    Add movement functions to the default pygame sprites.
    """
    def __init__(self):
        super().__init__()

    def update(self, *args):
        """
        A dummy function meant to be subclassed later.
        """
        pass

    def movex(self, xspeed):
        """
        Move the sprite in the X direction.
        Collisions are handled in the Room class, since the entire room
            needs to stop moving when a single Wall collides with the hero.
        Movement is split between X and Y so that collision checking only has to deal with
            one at a time.

        :param xspeed: Int representing the change in x direction
        """

        self.rect.x += xspeed

    def movey(self, yspeed):
        """
        Move the sprite in the Y direction.
        Collisions are handled in the Room class, since the entire room
            needs to stop moving when a single Wall collides with the hero.
        Movement is split between X and Y so that collision checking only has to deal with
            one at a time.

        :param yspeed:  Int representing the change in y direction
        """

        self.rect.y += yspeed


class Queue:
    """
    A wrapper for deque to make handling A* more legible

    Thanks to redblobgames for the basis of this code
    """
    def __init__(self):
        self.elements = collections.deque()

    def is_empty(self):
        """
        Return True if and only if the Queue is empty.
        """
        return len(self.elements) == 0

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


def load(imagename, subfolder=None):
    """
    Retrieves previously loaded images from _image_library, and stores newly created ones there as they are called.

    :param imagename: a string representing the name of the image to load, including extension
    :param subfolder: a string representing the subfolder in which the image is stored
    :returns image: a pygame surface created from the file at imagename

    thanks to Blake at NerdParadise for the basis of this code.
    """
    global _image_library
    image = _image_library.get((imagename, subfolder))

    if image is None:
        if subfolder:
            image = pygame.image.load(os.path.join("Sprites", subfolder, imagename)).convert_alpha()
        else:
            image = pygame.image.load(os.path.join("Sprites", imagename)).convert_alpha()
        _image_library[(imagename, subfolder)] = image

    return image


def create_background(background_tile):
    """
    Creates a surface made by tiling the background_tile image. Not stored in cache to allow background changes

    :param background_tile: a pygame surface that can be tiled
    :returns background: a pygame surface consisting of the tiled background_tile
    """
    background = pygame.Surface(settings['SCREEN_RESOLUTION'])
    for i in range(0, settings['WIDTH'], background_tile.get_width()):
        for n in range(0, settings['HEIGHT'], background_tile.get_height()):
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
        font = pygame.font.Font(os.path.join('Fonts', fontname), size)
        _font_library[(fontname, size)] = font

    return font


def play_music(musicname):
    """
    Load a pygame music object from a music file and play it.

    Called inside of gamestates.py as background music if and only if the PLAY_MUSIC setting is True

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
    rect.centerx = screen.get_rect().centerx
    rect.centery = .125*(position + 1)*settings['HEIGHT']
    screen.blit(text, rect)

    return rect


def create_menu(screen, title, options, descriptions=None,
                title_font=None, option_font=None, description_font=None,
                title_color=c.BLACK, option_color=c.BLACK,
                description_color=c.BLACK):
    """
    Dynamically create a menu of options for the user to move between.

    :param screen: The screen to blit to
    :param title: A title string to display at the top of the menu
    :param options: A list of strings showing option text
    :param descriptions: A list of strings describing the options. Gets displayed immediately below them
    :param title_font: The pre-loaded font to write the title with, if none, defaults to Melma size 48
    :param option_font: The pre-loaded font to write with, if none, will default to Melma size 32
    :param description_font: The preloaded font to write descriptions with, if none, defaults to Melma size 24
    :param title_color: The color to write the title in, defaults to black
    :param option_color: The color to write the options in, defaults to black
    :param description_color: The color to write descriptions in, defaults to black
    :returns rect_list: A list containing the containing rects for each option. Used to show the current selection
    """
    if title_font is not None:
        title_font = title_font
    else:
        title_font = load_font('Melma.ttf', 48)

    if option_font is not None:
        option_font = option_font
    else:
        option_font = load_font('Melma.ttf', 32)

    if description_font is not None:
        description_font = description_font
    else:
        description_font = load_font('Melma.ttf', 24)

    title_surf = title_font.render(title, 1, title_color)
    blit_text(title_surf, screen, 0)

    i = 1
    rect_list = []
    if descriptions is not None:
        for option in options:
            option_surf = option_font.render(option, 1, option_color)
            rect = blit_text(option_surf, screen, i)

            description_surf = description_font.render(descriptions[i - 1], 1, description_color)
            desc_rect = description_surf.get_rect()
            desc_rect.top = rect.bottom
            desc_rect.centerx = rect.centerx
            screen.blit(description_surf, desc_rect)

            rect_list.append(rect)
            i += 1
    else:
        for option in options:
            option_surf = option_font.render(option, 1, option_color)
            rect = blit_text(option_surf, screen, i)
            rect_list.append(rect)
            i += 1

    return rect_list