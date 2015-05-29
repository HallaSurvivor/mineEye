"""
Adds the Room class which stores data about any room that can be called via random generation.

Adds individual subclasses of Room with information specific to each room.
"""
import pygame
import config
import helpers as h


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

        self.xspeed = 0
        self.yspeed = 0

        self.xgravity = 0
        self.ygravity = 0

        self.room_array = None

        self.array_parsed = False

    def move_world(self, hero, x, y):
        """
        Move all of the blocks based on user input,
        Check for collisions.
        :param hero: An instance of the Hero class that walls can collide with.
        :param x: The Int of how far to shift the world's x
        :param y: the Int of how far to shift the world's y
        """

        # Move the blocks in the X direction
        for block in self.block_list:
            block.movex(x)

        # Check for block-hero collisions
        block_hit_list = pygame.sprite.spritecollide(hero, self.block_list, False)
        for block in block_hit_list:
            old_x_pos = block.rect.x
            if x > 0:
                block.rect.right = hero.rect.left
            elif x < 0:
                block.rect.left = hero.rect.right
            x_pos_change = block.rect.x - old_x_pos

            # Shift the rest of the room to stay in line with the block that collided
            for block2 in self.block_list:
                if block2 != block:
                    block2.rect.x += x_pos_change

            # Damage the player if the block is a spike
            if block.damage_player:
                hero.damage(5)

        # Move the blocks in the Y direction
        for block in self.block_list:
            block.movey(y)

        # Check for block-hero collisions
        block_hit_list = pygame.sprite.spritecollide(hero, self.block_list, False)
        for block in block_hit_list:
            old_y_pos = block.rect.y
            if y > 0:
                block.rect.bottom = hero.rect.top
            elif y < 0:
                block.rect.top = hero.rect.bottom
            y_pos_change = block.rect.y - old_y_pos

            # Shift the rest of the room to stay in line with the block that collided
            for block2 in self.block_list:
                if block2 != block:
                    block2.rect.y += y_pos_change

            # Damage the player if the block is a spike
            if block.damage_player:
                hero.damage(5)

    def change_gravity(self, changex, changey):
        """
        Change self.xgravity and self.ygravity to change the world's gravity.
        :param changex: the Int amount by which to change self.xgravity
        :param changey: the Int amount by which to change self.ygravity
        """
        self.xgravity += changex
        self.ygravity += changey

    def update(self, hero):
        """
        Update all of the blocks in the room,
        Update all of the enemies.
        :param hero: An instance of the Hero class to pass to self.move_world()
        """

        # Control the world via user input
        self.move_world(hero, self.xspeed, self.yspeed)

        # Move the world due to gravity
        self.move_world(hero, self.xgravity, self.ygravity)

        # Update all the blocks in the room
        self.block_list.update()

        # Update the enemies (not currently implemented)
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

    def changespeed(self, changex, changey):
        """
        Change the Room's velocity vector.
        :param changex: Int representing the amount by which to change self.xspeed
        :param changey: Int representing the amount by which to change self.yspeed
        """
        self.xspeed += changex
        self.yspeed += changey

    def parse_room_array(self):
        """
        Turn the list of strings stored in every room into an array of walls and enemies.
        """
        x = 0
        y = 256
        for row in self.room_array:
            for col in row:
                if col == "S":
                    wall = Wall(x, y, h.load('stone.png'))
                    self.block_list.add(wall)

                elif col == "P":
                    wall = Wall(x, y, h.load('spikes.png'), True)
                    self.block_list.add(wall)
                x += 64
            y += 64
            x = 0


class Room_01(Room):
    """
    Room 1
    """

    def __init__(self):
        super().__init__()

        self.background = h.create_background(h.load('background.png'))

        self.room_array = [
            "  SSDDSSSSSSSS  ",
            "  S          P  ",
            "  S          P  ",
            "  SSSSSSSSSDDS  ",
        ]


class Room_02(Room):
    """
    Room 2
    """
    def __init__(self):
        super().__init__()

        self.background = h.create_background(h.load('background.png'))

        self.room_array = [
            "  SSSSSSSSSDDS  ",
            "  P          P  ",
            "  P       S  P  ",
            "  SSDDSSSSSSSS  ",
        ]