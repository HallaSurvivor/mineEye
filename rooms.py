"""
Adds the Room class which stores data about any room that can be called via random generation.

Adds individual subclasses of Room with information specific to each room.
"""
import pygame
import config
import spritenames


class Room(object):
    """
    A superclass to define rooms.

    block_list is a sprite group comprising all blocks in a given level instance
    enemy_list is a sprite group comprising all the enemies in a given level instance

    background is a pygame Surface that is displayed behind the level

    region is a value representing what part of the mine the hero is in.
        This effects color scheme, block types, potential enemies, etc.

    TODO - make a key of what ascii characters corrosponds to which type of block and put it here
    """

    block_list = None
    enemy_list = None

    background = None

    region = None

    def __init__(self):
        """
        Set the blocklist and enemylist to be sprite groups, and the backgorund to be a surface.
        """
        self.block_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()

        self.background = pygame.Surface(config.SCREEN_RESOLUTION)

    def update(self):
        """
        Update everything in the room
        """
        self.block_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """
        Draw everything in the room
        :param screen: A pygame surface to blit everything onto.
        """
        screen.blit(self.background, (0, 0))

        self.block_list.draw(screen)
        self.enemy_list.draw(screen)


class Room_01(Room):
    """
    Room 1:

    TODO - make a schematic for this room and put it here.
    """

    def __init__(self):
        super().__init__()

        self.background = spritenames.create_background('background.png')

        room_array = [
            #[x_coord, y_coord, picture],
            []
        ]
        #TODO: Make some sort of parser to turn a txt file into a new room?

        for block in room_array:
            wall = spritenames.Wall(block[0], block[1], block[2])
            self.block_list.add(wall)
