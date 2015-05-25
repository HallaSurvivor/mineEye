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

        room_array is a list of strings that will be rendered into the room
        """
        self.block_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()

        self.background = pygame.Surface(config.SCREEN_RESOLUTION)

        self.room_array = None

        self.array_parsed = False

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
        if not self.array_parsed:
            self.parse_room_array()
            self.array_parsed = True

        self.block_list.draw(screen)
        self.enemy_list.draw(screen)

    def parse_room_array(self):
        """
        Turn the list of strings stored in every room into an array of walls and enemies.
        """
        x = 0
        y = 0
        for row in self.room_array:
            for col in row:
                if col == "S":
                    wall = spritenames.Wall(x, y, spritenames.load('stone.png'))
                    self.block_list.add(wall)

                elif col == "P":
                    wall = spritenames.Wall(x, y, spritenames.load('spikes.png'), True)
                    self.block_list.add(wall)
                x += 64
            y += 64
            x = 0


class Room_01(Room):
    """
    Room 1:

    TODO - make a schematic for this room and put it here.
    """

    def __init__(self):
        super().__init__()

        self.background = spritenames.create_background(spritenames.load('background.png'))

        self.room_array = [
            "SS  SSSSSSSSSSSS",
            "S              S",
            "S              S",
            "SSSSSSSSSSSSS  S",
        ]