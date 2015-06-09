"""
Adds the Room class which stores data about any room that can be called via random generation.

Adds individual subclasses of Room with information specific to each room.
"""
import random
from math import hypot
import pygame
from config import settings
import enemy
import weapons
import helpers as h

MoveRight = 0
MoveLeft = 1
MoveDown = 2

room_dict = {
    # A dictionary of all the rooms to randomly select from.
    # Each entry takes the form:
    # ROOM_NAME: [PrimaryPlayerMotion, *room_layout]
    # The First room must be StartingRoom,
    # The Second room must be EndingRoom
    "StartingRoom": [MoveRight,
                     "SSSSSSSS",
                     "S      S",
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
               "P       S  P",
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
               "S     BB   S",
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
            contents.append(random.choice(weapons.all_weapons))
            if hero.multiple_weapon_drops:
                contents.append(random.choice(weapons.all_weapons))
        elif self.is_item_chest:
            pass

        return contents


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
        B is a breakable wall
        R is a turret
        T is a block that stops the timer
        W is a weapon chest
        D is door <- IMPORTANT, you need a door at the top and bottom to make the logic work
    """

    block_list = None
    chest_list = None
    enemy_list = None
    enemy_projectile_list = None
    hero_projectile_list = None
    bomb_list = None

    background = None

    region = None

    def __init__(self):
        """
        Set the blocklist and enemylist to be sprite groups, and the background to be a surface.

        room_array is a list of strings that will be rendered into the room
        """
        self.all_sprites = pygame.sprite.Group()
        self.block_list = pygame.sprite.Group()
        self.chest_list = pygame.sprite.Group()
        self.drops_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.enemy_projectile_list = pygame.sprite.Group()
        self.hero_projectile_list = pygame.sprite.Group()
        self.bomb_list = pygame.sprite.Group()

        self.background = pygame.Surface(settings['SCREEN_RESOLUTION'])

        self.xspeed = 0
        self.yspeed = 0

        self.base_y_gravity = -3
        self.gravity_acceleration = -1

        self.room_array = []

        self.array_parsed = False

    def move_world(self, hero, x, y):
        """
        Move all of the blocks by x and y,
        Check for collisions.
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
                hero.damage(block.damage)

            # End the game timer if the block is the end
            if block.end_timer:
                hero.run_timer = False

        # Deal contact damage with enemies
        enemy_hit_list = pygame.sprite.spritecollide(hero, self.enemy_list, False)
        for e in enemy_hit_list:
            if e.contact_damage:
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
                self.all_sprites.add(thing)

            chest.kill()

    def cause_ranged_attacks(self, hero):
        """
        Cause every enemy with a ranged attack to attack the hero, if in range
        :param hero: The hero to target
        """
        for e in self.enemy_list:
            distance = hypot(e.rect.centerx - hero.rect.centerx, e.rect.centery - hero.rect.centery)
            if e.is_ranged and distance < e.attack_range:
                if e.ranged_attack_cooldown == 0:
                    proj = e.ranged_attack(hero)
                    self.enemy_projectile_list.add(proj)
                    self.all_sprites.add(proj)
                else:
                    e.ranged_attack_cooldown -= 1

    def destroy_projectiles(self):
        """
        Check collisions between projectiles and walls, and destroy projectiles appropriately.
        """
        for block in self.block_list:
            hit_list = pygame.sprite.spritecollide(block, self.enemy_projectile_list, False)
            for proj in hit_list:
                proj.kill()

        for proj in self.enemy_projectile_list:
            hit_list = pygame.sprite.spritecollide(proj, self.hero_projectile_list, False) # Remove the hero proj too
            if len(hit_list) > 0:
                proj.kill()
            for hero_proj in hit_list:
                hero_proj.kill()

    def det_bombs(self, hero):
        """
        Check collisions between bombs and walls, and have them stick until they detonate.
        """
        for bomb in self.bomb_list:
            hit_list = pygame.sprite.spritecollide(bomb, self.block_list, False)
            if len(hit_list) > 0:
                for block in self.block_list:
                    distance = hypot(block.rect.centerx - bomb.rect.centerx, block.rect.centery - bomb.rect.centery)
                    if distance < bomb.radius and block.breakable:
                        block.kill()

                for e in self.enemy_list:
                    distance = hypot(e.rect.centerx - bomb.rect.centerx, e.rect.centery - bomb.rect.centery)
                    if distance < bomb.radius:
                        if not hero.bomb_control:
                            e.damage(100)
                        else:
                            e.damage(150)

                for chest in self.chest_list:
                    distance = hypot(chest.rect.centerx - bomb.rect.centerx, chest.rect.centery - bomb.rect.centery)
                    if distance < bomb.radius:
                        if not hero.bomb_control:
                            chest.kill()

                hero_distance = hypot(hero.rect.centerx - bomb.rect.centerx, hero.rect.centery - bomb.rect.centery)
                if hero_distance < bomb.radius:
                    if not hero.bomb_control:
                        hero.damage(25)

                bomb.kill()

    def cause_projectile_damage(self, hero):
        """
        Cause damage to the player from projectiles
        :param hero: The hero to check against the projectiles, and damage for a hit.
        """
        hit_list = pygame.sprite.spritecollide(hero, self.enemy_projectile_list, True)
        for proj in hit_list:
            hero.damage(proj.damage)

    def update(self, hero):
        """
        Update all of the blocks in the room,
        Update all of the enemies.
        :param hero: An instance of the Hero class to pass to self.move_world()
        """
        # Calculate the effect of gravity
        self.calc_gravity()

        #Stick the bombs to walls
        self.det_bombs(hero)

        # Control the world via user input
        self.move_world(hero, self.xspeed, self.yspeed)

        # Update all the blocks in the room
        self.block_list.update()
        self.bomb_list.update(0, self.gravity_acceleration)

        # Remove enemies that are dead
        for e in self.enemy_list:
            if e.current_hp <= 0:
                self.enemy_list.remove(e)
                self.all_sprites.remove(e)

        # Use ranged attacks
        self.cause_ranged_attacks(hero)

        # Deal damage from ranged attacks
        self.cause_projectile_damage(hero)

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
        screen.blit(self.background, (0, 0))

        if not self.array_parsed:
            self.parse_room_array(settings['SCREEN_RESOLUTION'][0] / 2 - 128, settings['SCREEN_RESOLUTION'][1] / 2 - 128)

        self.all_sprites.draw(screen)

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
        :param xstart: Int representing the starting x location
        :param ystart: Int representing the starting y location
        """
        x = xstart
        y = ystart
        for row in self.room_array:
            if row != MoveRight and row != MoveLeft and row != MoveDown:
                for col in row:
                    if col == "S":
                        wall = Wall(x, y, h.load('stone.png'))
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)

                    if col == "T":
                        wall = Wall(x, y, h.load('stone.png'), end_timer=True)
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)

                    elif col == "P":
                        wall = Wall(x, y, h.load('spikes.png'), damage_player=True)
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)

                    elif col == "B":
                        wall = Wall(x, y, h.load('broken_stone.png'), breakable=True)
                        self.block_list.add(wall)
                        self.all_sprites.add(wall)

                    elif col == "R":
                        new_enemy = enemy.Turret()
                        new_enemy.rect.x = x + 8
                        new_enemy.rect.y = y + 16
                        self.enemy_list.add(new_enemy)
                        self.all_sprites.add(new_enemy)

                    elif col == "W":
                        chest = Chest(x, y, weapon=True)
                        chest.rect.x += 8
                        chest.rect.y += 16
                        self.chest_list.add(chest)
                        self.all_sprites.add(chest)

                    x += 64
                y += 64
                x = xstart

        self.array_parsed = True


class World(Room):
    """
    The complete world to be drawn to the screen.
    """

    def __init__(self, rooms):
        """
        Initialize the world.
        :param rooms: A list of all the Room objects in the order they appear.
        """
        super().__init__()
        self.background = h.create_background(h.load('background.png'))

        self.room_array = []
        for room in rooms:
            if len(self.room_array) == 0:
                self.room_array += room

            else:
                previous_door_location = 0
                for char in self.room_array[-1]:
                    previous_door_location += 1
                    if char == "D":
                        break

                new_door_location = 0
                for char in room[1]:
                    if char != MoveDown and char != MoveLeft and char != MoveRight:
                        new_door_location += 1
                    if char == "D":
                        break

                door_location = previous_door_location - new_door_location

                aligned_room = []
                for row in room:
                    if type(row) == str:
                        aligned_row = ""
                        for s in range(door_location):
                            aligned_row += " "
                        aligned_row += row
                        aligned_room.append(aligned_row)

                self.room_array += aligned_room