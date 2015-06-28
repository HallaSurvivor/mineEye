"""
Adds the room_dict dictionary, storing the room layouts, as well as the Room() class, which parses those layouts

room_dict is a dictionary of lists of strings, where each list begins
with a header describing the direction of motion in the room.
This list of strings is then parsed character by character to create the
walls, enemies, and chests that make up the world.

World is a Room created by putting groups of room_dict items next to each other.
This larger room, comprised of a semi-random selection of the rooms inside room_dict,
is what makes up the Hero's world. The semi-random generation takes place inside gamestates.py
"""
import random
import logging
from math import hypot
import pygame
from config import settings
import enemy
import drops
import helpers as h

module_logger = logging.getLogger('mineEye.rooms')

MoveRight = 0
MoveLeft = 1
MoveDown = 2

room_dict = {
    # A dictionary of all the rooms to randomly select from.
    # Each entry takes the form:
    # ROOM_NAME: [PrimaryPlayerMotion, *room_layout]
    # StartingRoom and EndingRoom must exist somewhere
    "StartingRoom": [MoveRight,
                     "SSSSSSSS",
                     "S     FS",
                     "SW     S",
                     "SSSSSDDS"
    ],
    "EndingRoom": [MoveDown,
                   "SSSDDSSS",
                   "S      S",
                   "S      S",
                   "SP    PS",
                   "P      P",
                   "SSTTTTSS"
    ],
    "Room01": [MoveDown,
               "SSDDSS",
               "S    S",
               "S    S",
               "SS   S",
               "S    S",
               "S   SS",
               "S    S",
               "S S SS",
               "S    S",
               "S    S",
               "SSDDSS"
    ],
    "Room02": [MoveLeft,
               "SSSSSSSSSDDS",
               "P          P",
               "P      WS  P",
               "SSDDSSSSSSSS",
    ],
    "Room03": [MoveRight,
               "SSDDSSSSSSSS",
               "S          P",
               "S     B    P",
               "SSSSSSSSSDDS",
    ],
    "Room04": [MoveRight,
               "SSDDSSSSSSSSSSSSS",
               "S               S",
               "SR              S",
               "S     SSSSSSS   S",
               "S      S   S    S",
               "S    S R S      S",
               "SSSSSSSSSSSSSDDSS"
    ],
    "Room05": [MoveLeft,
                "SSSSSSSSSSSSSSSDDS",
                "S                S",
                "S                S",
                "S                S",
                "S   SSSSSSSSP  SSS",
                "S    S   S   S   S",
                "S  B   B   B     S",
                "SDDSSSSSSSSSSSSSSS"
    ],
    "Room06": [MoveRight,
               "SSDDSSSSSSSS",
               "S          S",
               "S      B   S",
               "S  G  BB   S",
               "SSSSSSSSDDSS"
    ],
    "Room07": [MoveDown,
               "SSDDSS",
               "S    S",
               "S    S",
               "S    S",
               "S    S",
               "SR  RS",
               "S    S",
               "S BBBS",
               "S    S",
               "SBBB S",
               "S    S",
               "S    S",
               "SSDDSS"
    ],
    "Room08": [MoveLeft,
               "SSSSSSSSSSSDDSSS",
               "S       R      S",
               "S   B          S",
               "SS  BB         S",
               "SSDDSSSSSSSSSSSS"

    ]
}


class Wall(h.Sprite):
    """
    Wall the Hero can collide with.

    self.damage_player is True if the player is hurt on contact (spikes) but False otherwise
    """

    def __init__(self, x, y, image, damage_player=False, end_timer=False, breakable=False, damage=1):
        """
        Create the wall and its location
        :param x: Int representing the x position of the wall's top left corner
        :param y: Int representing the y position of the wall's top left corner
        :param image: a pygame surface associated with the wall's texture
        :param damage_player: Boolean. True if touching the wall hurts the player
        :param end_timer: Boolean. True if touching the wall ends the game timer.
        :param breakable: Boolean. True if the player's explosives can destroy the wall.
        :param damage: Int. The amount of damage per tick to deal.
        """
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

        self.damage = damage
        self.damage_player = damage_player
        self.end_timer = end_timer

        self.breakable = breakable


class Chest(h.Sprite):
    """
    A chest that can hold either items or weapons.
    """

    def __init__(self, x, y, item=False, weapon=False):
        """
        Create the chest.
        :param x: Int representing the x position of the chest's top left corner
        :param y: Int representing the y position of the chest's top left corner
        :param item: Bool. True if the chest has an item. False by default
        :param weapon: Bool. True of the chest has a weapon. False by default
        """
        super().__init__()

        self.image = h.load('chest.png')
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.is_item_chest = item
        self.is_weapon_chest = weapon

    def generate_contents(self, hero):
        """
        Generate an item/weapon when the chest is opened. Called in Room.check_chests()
        :param hero: The hero opening the chest. Hero could have attributes modifying item drops.
        :returns contents: A list of sprites representing the items/weapons in the chest.
        """
        contents = []
        if self.is_weapon_chest:
            contents.append(random.choice(drops.all_weapons)(self.rect.center))
            if hero.multiple_weapon_drops:
                contents.append(random.choice(drops.all_weapons)(self.rect.center))
        elif self.is_item_chest:
            pass
        return contents


class Room:
    """
    A superclass to define rooms.

    Sprite Groups:
        block_list comprises all the walls
        chest_list comprises all the chests
        drops_list comprises all the weapons/items on the floor
        enemy_list comprises all the enemies
        enemy_projectile_list comprises all the shots fired by the enemy
        hero_projectile_list comprises all the shots fired by the hero
        bomb_list comprises all the bombs thrown by the hero

        all_sprite_list comprises all the sprites that move alongside the world.

    Pathfinding:
        Enemies use A* pathfinding to navigate the world.
        Because of this, a set of nodes corresponding to the centers of tiles
        is added.

    background is a pygame Surface that is displayed behind the level

    region is a value representing what part of the mine the hero is in.
        This effects color scheme, block types, potential enemies, etc.

    KEY for room_array:
        S is stone
        P is spike
        B is a breakable wall
        R is a turret
        G is a ghost
        T is a block that stops the timer
        W is a weapon chest
        D is door <- IMPORTANT, you need a door at the top and bottom to make the logic work
    """

    def __init__(self, seed=None):
        """
        Create the room based on a certain room_array

        room_array is a list of strings that will be rendered into the room

        :param seed: The seed to use to generate the world. Passed from
            the generateworld() operation to allow for users to save everything
            about a room.
        """

        self.logger = logging.getLogger('mineEye.rooms.Room')

        self.seed = seed
        random.seed(self.seed)

        self.all_sprites = pygame.sprite.Group()
        self.block_list = pygame.sprite.Group()
        self.chest_list = pygame.sprite.Group()
        self.drops_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.enemy_projectile_list = pygame.sprite.Group()
        self.hero_projectile_list = pygame.sprite.Group()
        self.bomb_list = pygame.sprite.Group()

        self.nodes = h.Graph()

        self.background_string = ''
        self.background = pygame.Surface(settings['SCREEN_RESOLUTION'])
        self.region = None

        self.xspeed = 0
        self.yspeed = 0

        self.base_y_gravity = -3
        self.gravity_acceleration = -1

        self.room_array = []

        self.array_parsed = False

    def update(self, hero):
        """
        Cause all of the effects and changes that take place between game ticks

        :param hero: An instance of the Hero class to pass to self.move_world()
        """
        # Calculate the effect of gravity
        self.calc_gravity()

        # Move the player's bombs through the world
        self.cause_bomb_gravity()

        #Blow up the bombs that hit walls
        self.det_bombs(hero)

        # Control the world via user input and gravity
        self.move_world(hero, self.xspeed, self.yspeed)

        # Update all the blocks in the room
        self.block_list.update()

        # Check if the player hit a chest
        self.check_chests(hero)

        # Make the chest's drops follow gravity
        self.cause_dropped_item_gravity()

        # Use ranged attacks
        self.cause_ranged_attacks(hero)

        # Deal damage from ranged attacks
        self.cause_projectile_damage(hero)

        # Deal contact damage
        self.cause_contact_damage(hero)

        # Update the enemies
        self.enemy_list.update(hero)

        # Destroy any projectiles that hit walls or opposing projectiles
        self.destroy_projectiles()

        #Update the entities
        self.enemy_projectile_list.update()

    def draw(self, screen):
        """
        Draw everything in the room

        :param screen: A pygame surface to blit everything onto.
        """
        if self.background.get_size() != screen.get_size():
            self.background = h.create_background(h.load(self.background_string))
        screen.blit(self.background, (0, 0))

        if not self.array_parsed:
            # Create the room 128, 128 left and upwards of center-screen
            self.parse_room_array(settings['SCREEN_RESOLUTION'][0] / 2 - 128,
                                  settings['SCREEN_RESOLUTION'][1] / 2 - 128)

        self.all_sprites.draw(screen)

    def move_world(self, hero, x, y):
        """
        Move the world based on Hero speed and user input

        first move by x,
        check for collisions,
        stop the world moving if the hero collides with the world,
        damage the hero if standing on a spike,
        repeat for moving by y

        :param hero: An instance of the Hero class that walls can collide with.
        :param x: The Int of how far to shift the world's x
        :param y: the Int of how far to shift the world's y
        """

        # Move the blocks in the X direction
        for sprite in self.all_sprites:
            sprite.movex(x)

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
            for sprite in self.all_sprites:
                if sprite != block:
                    sprite.rect.x += x_pos_change

            # Damage the player if the block is a spike
            if block.damage_player:
                self.logger.info('player touched spike')
                hero.damage(block.damage)

            # End the game timer if the block is the end
            if block.end_timer:
                hero.run_timer = False

        # Move the blocks in the Y direction
        for sprite in self.all_sprites:
            sprite.movey(y)

        # Check for block-hero collisions
        block_hit_list = pygame.sprite.spritecollide(hero, self.block_list, False)
        for block in block_hit_list:
            old_y_pos = block.rect.y

            if hero.take_falldamage:
                damage = -self.yspeed - 50
                if damage > 0:
                    self.logger.info('hero took fall damage')
                    hero.damage(damage)

            if y > 0:
                block.rect.bottom = hero.rect.top
            elif y < 0:
                block.rect.top = hero.rect.bottom
                self.yspeed = 0
                hero.jumping = False
                hero.double_jumping = False

            y_pos_change = block.rect.y - old_y_pos

            # Shift the rest of the room to stay in line with the block that collided
            for sprite in self.all_sprites:
                if sprite != block:
                    sprite.rect.y += y_pos_change

            # Damage the player if the block is a spike
            if block.damage_player:
                self.logger.info('player touched spike')
                hero.damage(block.damage)

            # End the game timer if the block is the end
            if block.end_timer:
                hero.run_timer = False

    def cause_contact_damage(self, hero):
        """
        Damage the hero if he collides with an enemy dealing contact damage

        :param hero: A hero to damage
        """
        enemy_hit_list = pygame.sprite.spritecollide(hero, self.enemy_list, False)
        for e in enemy_hit_list:
            if e.contact_damage:
                self.logger.info('contact damage - {0}'.format(e))
                hero.damage(e.contact_damage)

    def calc_gravity(self):
        """
        Change self.yspeed to cause an acceleration due to gravity.
        """
        if self.yspeed == 0:
            self.yspeed = self.base_y_gravity
        else:
            self.yspeed += self.gravity_acceleration

    def check_chests(self, hero):
        """
        Check for a collision between the chest and a hero and spawn the proper item if a collision happens.

        :param hero: The hero to check against.
        """
        hit_list = pygame.sprite.spritecollide(hero, self.chest_list, False)
        for chest in hit_list:
            contents = chest.generate_contents(hero)
            for thing in contents:
                self.all_sprites.add(thing.sprite)
                self.drops_list.add(thing.sprite)

            chest.kill()

    def cause_dropped_item_gravity(self):
        """
        Cause gravity for drops and stop any dropping items/weapons from falling through the floor.
        """
        for drop in self.drops_list:
            drop.movex(drop.changex)
            hit_list = pygame.sprite.spritecollide(drop, self.block_list, False)
            for block in hit_list:
                if drop.changex > 0:
                    drop.rect.right = block.rect.left
                elif drop.changex < 0:
                    drop.rect.left = block.rect.right
                drop.changex = 0

            if drop.changey == 0:
                drop.changey = -self.base_y_gravity
            else:
                drop.changey -= self.gravity_acceleration

            drop.movey(drop.changey)
            hit_list = pygame.sprite.spritecollide(drop, self.block_list, False)
            for block in hit_list:
                if drop.changey > 0:
                    drop.rect.bottom = block.rect.top
                elif drop.changey < 0:
                    drop.rect.top = block.rect.bottom
                drop.changey = 0
                drop.changex = 0

    def cause_ranged_attacks(self, hero):
        """
        Cause every enemy with a ranged attack to attack the hero, if within range

        :param hero: The hero to target
        """
        for e in self.enemy_list:
            distance = hypot(e.rect.centerx - hero.rect.centerx, e.rect.centery - hero.rect.centery)
            if e.is_ranged and distance <= e.attack_range:
                if e.cooldown == 0:
                    proj = e.ranged_attack(hero)
                    self.enemy_projectile_list.add(proj)
                    self.all_sprites.add(proj)
                else:
                    e.cooldown -= 1

    def destroy_projectiles(self):
        """
        Destroy projectiles that should be destroyed.

        This includes projectiles hitting walls, and hero projectiles hitting enemy projectiles
        """
        for block in self.block_list:
            hit_list = pygame.sprite.spritecollide(block, self.enemy_projectile_list, False)
            for proj in hit_list:
                self.logger.debug('destroyed projectile fired by {0} because it hit a wall'.format(proj.owner))
                proj.kill()

        for proj in self.enemy_projectile_list:
            hit_list = pygame.sprite.spritecollide(proj, self.hero_projectile_list, False)
            if len(hit_list) > 0:
                self.logger.debug('destroyed enemy projectile fired by {0} because it hit a player projectile'.format(proj.owner))
                proj.kill()
            for hero_proj in hit_list:
                self.logger.debug('destroyed player projectile because it hit an enemy projectile')
                hero_proj.kill()

    def det_bombs(self, hero):
        """
        Check collisions between bombs and walls, and have them detonate, damaging things within their explosion radius.

        Destroy breakable walls
        Damage enemies
        If the hero doesn't have bomb_control:
            Destroy chests
            Damage the Hero
        """
        for bomb in self.bomb_list:
            hit_list = pygame.sprite.spritecollide(bomb, self.block_list, False)
            if len(hit_list) > 0:
                for block in self.block_list:
                    distance = hypot(block.rect.centerx - bomb.rect.centerx, block.rect.centery - bomb.rect.centery)
                    if distance < bomb.radius and block.breakable:
                        self.logger.info('destroyed block at {0} with bomb'.format((block.rect.x, block.rect.y)))
                        self.nodes.make_passable([block.rect.centerx, block.rect.centery])
                        block.kill()

                for e in self.enemy_list:
                    distance = hypot(e.rect.centerx - bomb.rect.centerx, e.rect.centery - bomb.rect.centery)
                    if distance < bomb.radius:
                        self.logger.info('damaged {0} with bomb'.format(e))
                        if not hero.bomb_control:
                            e.damage(100)
                        else:
                            e.damage(150)

                for chest in self.chest_list:
                    distance = hypot(chest.rect.centerx - bomb.rect.centerx, chest.rect.centery - bomb.rect.centery)
                    if distance < bomb.radius:
                        if not hero.bomb_control:
                            self.logger.info('destroyed chest at {0} with bomb'.format((chest.rect.x, chest.rect.y)))
                            chest.kill()

                hero_distance = hypot(hero.rect.centerx - bomb.rect.centerx, hero.rect.centery - bomb.rect.centery)
                if hero_distance < bomb.radius:
                    if not hero.bomb_control:
                        self.logger.info('damage self with bomb')
                        hero.damage(25)

                bomb.kill()

    def cause_bomb_gravity(self):
        """
        Make the bombs obey gravity regardless of world motion
        """
        for bomb in self.bomb_list:
            bomb.changey -= self.base_y_gravity
            bomb.movex(bomb.changex)
            bomb.movey(bomb.changey)

    def cause_projectile_damage(self, hero):
        """
        Cause damage to the player from projectiles

        :param hero: The hero to check against the projectiles, and damage for a hit.
        """
        hit_list = pygame.sprite.spritecollide(hero, self.enemy_projectile_list, True)
        for proj in hit_list:
            self.logger.info('Hero damaged by enemy projectile')
            hero.damage(proj.damage)

    def setspeed(self, setx, sety):
        """
        Set a new x and y speed instead of changing the current one.

        :param setx: Int representing the new self.xspeed
        :param sety: Int representing the new self.yspeed
        """
        if setx is not None:
            self.xspeed = setx
        if sety is not None:
            self.yspeed = sety

    def changespeed(self, changex, changey):
        """
        Change the Room's velocity vector.

        :param changex: Int representing the amount by which to change self.xspeed
        :param changey: Int representing the amount by which to change self.yspeed
        """
        self.xspeed += changex
        self.yspeed += changey

    def parse_room_array(self, xstart, ystart):
        """
        Turn a list of strings into an array of walls and enemies.

        Move top -> bottom through the rows, and go left -> through each character in a given row

        Add a block, enemy, chest, etc. with the characteristics below at a given position
        for each character in the room. Each block unit is 64x64 px

        KEY for room_array:
        S is stone
        P is spike
        B is a breakable wall
        R is a turret
        G is a ghost
        T is a block that stops the timer
        W is a weapon chest
        D is door <- IMPORTANT, you need a door at the top and bottom to make the logic work

        :param xstart: Int representing the starting x location
        :param ystart: Int representing the starting y location
        """
        x = xstart
        y = ystart
        for row in self.room_array:
            if row != MoveRight and row != MoveLeft and row != MoveDown:
                for col in row:
                    node = (x+32, y+32)  # +32 moves the node to the tile's center

                    if col == "S":
                        wall = Wall(x, y, h.load('stone.png'))
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)
                        self.nodes.add_wall(node)

                    if col == "T":
                        wall = Wall(x, y, h.load('stone.png'), end_timer=True)
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)
                        self.nodes.add_wall(node)

                    elif col == "P":
                        wall = Wall(x, y, h.load('spikes.png'), damage_player=True)
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)
                        self.nodes.add_wall(node)

                    elif col == "B":
                        wall = Wall(x, y, h.load('broken_stone.png'), breakable=True)
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)
                        self.nodes.add_wall(node)

                    elif col == "R":
                        new_enemy = enemy.Turret(self)
                        new_enemy.rect.center = node
                        self.enemy_list.add(new_enemy)
                        self.all_sprites.add(new_enemy)

                    elif col == "G":
                        new_enemy = enemy.Ghost(self)
                        new_enemy.rect.center = node
                        self.enemy_list.add(new_enemy)
                        self.all_sprites.add(new_enemy)

                    elif col == "F":
                        new_enemy = enemy.FireBat(self)
                        new_enemy.rect.center = node
                        self.enemy_list.add(new_enemy)
                        self.all_sprites.add(new_enemy)

                    elif col == "W":
                        chest = Chest(x, y, weapon=True)
                        chest.rect.x += 8
                        chest.rect.y += 16
                        self.chest_list.add(chest)
                        self.all_sprites.add(chest)

                    if col != "&":
                        self.nodes.append(node)
                    x += 64
                y += 64
                x = xstart

        self.array_parsed = True


class World(Room):
    """
    The complete world to be drawn to the screen.
    """

    def __init__(self, rooms, seed=None):
        """
        Initialize the world.

        * Cycle through the first door block at the bottom of the last room,
        * Then find the first door block at the top of the new room,
        * Finally add a bunch of blank characters (spaces) to offset the new room until
            the doors line up

        :param rooms: A list of all the Room objects in the order they appear.
        :param seed: The seed to use in random generation.
        """
        super().__init__(seed=seed)

        random.seed(seed)

        self.background_string = 'background.png'
        self.background = h.create_background(h.load(self.background_string))
        self.logger.debug('===Begin modifying rooms to align doors===')

        self.room_array = []
        for index, room in enumerate(rooms):
            self.logger.debug(' ')
            self.logger.debug('next room: {0}'.format(index))
            for row in room:
                if type(row) != int:
                    self.logger.debug(row)

            if len(self.room_array) == 0:
                self.room_array += room[1:]  # get rid of the leading "move right" identifier

            else:
                previous_door_location = 0
                for char in self.room_array[-1]:
                    previous_door_location += 1
                    if char == "D":
                        self.logger.debug("previous door location: {0}".format(previous_door_location))
                        break

                new_door_location = 0
                for char in room[1]:
                    if char != MoveDown and char != MoveLeft and char != MoveRight:
                        new_door_location += 1
                    if char == "D":
                        self.logger.debug("new door location: {0}".format(new_door_location))
                        break

                door_location = previous_door_location - new_door_location
                self.logger.debug('net door location (prev - new): {0}'.format(door_location))

                aligned_room = []
                for row in room:
                    # Add spaces (blank tile) to each row to line up its door with the previous room
                    if type(row) == str:
                        aligned_row = ""
                        for s in range(door_location):
                            aligned_row += "&"
                        aligned_row += row
                        aligned_room.append(aligned_row)

                self.room_array += aligned_room

        self.logger.info('----====Finished World====----')
        for row in self.room_array:
            self.logger.info(row.replace('&', ' '))
