"""Defines the load(imagename) function to import sprites into the game"""
import os
import pygame

_image_library = {}

def load(imagename):
    """Retrieves previously loaded images from _image_library, and stores newly created ones there as they are called.

    thanks to Blake at NerdParadise for the basis of this code.
    """
    global _image_library
    image = _image_library.get(imagename)

    if image is None:
        image = pygame.image.load(os.path.join("Sprites", imagename))
        _image_library[imagename] = image

    return image