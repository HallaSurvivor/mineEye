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

    world_shift_x represents how far to the left the world has moved to give a sense of motion
    world_shift_y represents how far up the world has moved to give a sense of motion

    region is a value representing what part of the mine the hero is in.
        This effects color scheme, block types, potential enemies, etc.

    KEY for room_array:
        S is stone
        P is spike
        D is door <- IMPORTANT, you need a door at the top and bottom to make the logic work
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

        self.world_shift_x = 0
        self.world_shift_y = 0

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

        self.shift_world()

        self.block_list.draw(screen)
        self.enemy_list.draw(screen)

    def parse_room_array(self):
        """
        Turn the list of strings stored in every room into an array of walls and enemies.
        """
        x = 0
        y = 256
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

    def shift_world(self):
        """
        Shift everything in the world by world_shift_x and world_shift_y, which parallel the hero's movespeed
        """
        for block in self.block_list:
            block.rect.x += self.world_shift_x
            block.rect.y += self.world_shift_y

        for enemy in self.enemy_list:
            enemy.rect.x += self.world_shift_x
            enemy.rect.y += self.world_shift_y


class Room_01(Room):
    """
    Room 1:

    TODO - make a schematic for this room and put it here.
    """

    def __init__(self):
        super().__init__()

        self.background = spritenames.create_background(spritenames.load('background.png'))

        self.room_array = [
            "  SSDDSSSSSSSS  ",
            "  S          P  ",
            "  S          P  ",
            "  SSSSSSSSSDDS  ",
        ]