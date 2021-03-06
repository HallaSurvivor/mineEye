"""
Stores the World and everything that takes place within it

World is created by putting rooms next to each other.
The semirandom selection for this generation takes place in
gamestates.InGame.generate_world()
"""
import random
import logging
import pygame
from config import settings
import enemy
import drops
import helpers as h

module_logger = logging.getLogger('mineEye.world')


class Wall(h.Sprite):
    """
    A wall that makes up the world.
    """

    def __init__(self, center, end_timer=False, breakable=False, damage=0):
        """
        Create the wall and its location
        :param center: the center of the sprite
        :param image: a pygame surface associated with the wall's texture
        :param damage_player: Boolean. True if touching the wall hurts the player
        :param end_timer: Boolean. True if touching the wall ends the game timer.
        :param breakable: Boolean. True if the player's explosives can destroy the wall.
        :param damage: Int. The amount of damage per tick to deal.
        """
        super().__init__()

        self.end_timer = end_timer
        self.breakable = breakable
        self.damage = damage

        if breakable:
            self.image = h.load('broken_stone.png')
        elif damage:
            self.image = h.load('spikes.png')
        else:
            self.image = h.load('stone.png')

        self.rect = self.image.get_rect()
        self.rect.center = center


class World:
    """
    Defines the World.

    Sprite Groups:
        block_list comprises all the walls
        chest_list comprises all the chests
        drops_list comprises all the weapons/items on the floor
        enemy_list comprises all the enemies
        enemy_projectile_list comprises all the shots fired by the enemy
        hero_projectile_list comprises all the shots fired by the hero
        bomb_list comprises all the bombs thrown by the hero

        all_sprites comprises all the sprites that move alongside the world.

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

        self.logger = logging.getLogger('mineEye.world.World')

        self.seed = seed
        random.seed(self.seed)

        self.run_timer = True

        self.all_sprites = pygame.sprite.Group()
        self.block_list = pygame.sprite.Group()
        self.spikes_list = pygame.sprite.Group()
        self.drops_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.enemy_projectile_list = pygame.sprite.Group()
        self.hero_projectile_list = pygame.sprite.Group()
        self.bomb_list = pygame.sprite.Group()

        self.nodes = h.Graph()

        self.background_string = 'background.png'
        self.background = h.create_background(h.load(self.background_string))
        self.region = None

        self.weapon_factor = 6  # tenths of a percent chance of spawning a weapon a a given node

        self.xspeed = 0
        self.yspeed = 0

        self.xshift = 0
        self.yshift = 0

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

        # Update the enemies
        self.enemy_list.update(hero)

        # Control the world via user input and gravity
        self.move_world(hero, self.xspeed, self.yspeed)

        # Cause spike damage
        self.cause_spike_damage(hero)

        # Update all the blocks in the room
        self.block_list.update()

        # Make the chest's drops follow gravity
        self.cause_dropped_item_gravity()

        # Use ranged attacks
        self.cause_ranged_attacks(hero)

        # Deal damage from ranged attacks
        self.cause_projectile_damage(hero)

        # Deal contact damage
        self.cause_contact_damage(hero)

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
            self.parse_room_array()
            self.add_weapons_to_world()

        for e in self.enemy_list:
            e.draw(screen)

        self.block_list.draw(screen)
        self.spikes_list.draw(screen)
        self.drops_list.draw(screen)
        self.enemy_projectile_list.draw(screen)
        self.hero_projectile_list.draw(screen)
        self.bomb_list.draw(screen)

    def _move_world_x(self, hero, x):
        """
        Move the blocks/nodes in the X direction

        move the entire world,
        check for collisions,
        stop the world moving if the hero collides with the world,
        damage the hero if standing on a spike,
        end the game if the hero is standing on a timer
        """
        self.nodes.shift_nodes_x(x)
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
            self.nodes.shift_nodes_x(x_pos_change)
            for sprite in self.all_sprites:
                if sprite != block:
                    sprite.rect.x += x_pos_change

            # End the game timer if the block is the end
            if block.end_timer:
                self.run_timer = False

    def _move_world_y(self, hero, y):
        """
        Move the blocks/nodes in the Y direction

        move the entire world,
        check for collisions,
        stop the world moving if the hero collides with the world,
        damage the hero if standing on a spike,
        end the game if the hero is standing on a timer
        """
        self.nodes.shift_nodes_y(y)
        for sprite in self.all_sprites:
            sprite.movey(y)

        # Check for block-hero collisions
        block_hit_list = pygame.sprite.spritecollide(hero, self.block_list, False)
        if len(block_hit_list) > 0:

            if hero.take_falldamage:
                damage = -self.yspeed - 25
                if damage > 0:
                    self.logger.info('hero took fall damage')
                    hero.damage(damage)

            self.changespeed(0, -self.yspeed)

        for block in block_hit_list:
            old_y_pos = block.rect.y

            if y > 0:
                block.rect.bottom = hero.rect.top
                self.logger.debug('Hero clipped with the ceiling')
            elif y < 0:
                block.rect.top = hero.rect.bottom
                self.logger.debug('Hero clipped with the floor')
                self.yspeed = 0
                hero.jumping = False
                hero.double_jumping = False

            y_pos_change = block.rect.y - old_y_pos

            # Shift the rest of the room to stay in line with the block that collided
            self.nodes.shift_nodes_y(y_pos_change)
            for sprite in self.all_sprites:
                if sprite != block:
                    sprite.rect.y += y_pos_change

            # End the game timer if the block is the end
            if block.end_timer:
                self.run_timer = False

    def move_world(self, hero, x, y):
        """
        Move the world based on Hero speed and user input

        move by X, then Y

        :param hero: An instance of the Hero class that walls can collide with.
        :param x: The Int of how far to shift the world's x
        :param y: the Int of how far to shift the world's y
        """

        self._move_world_x(hero, x)
        self._move_world_y(hero, y)

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

    def cause_spike_damage(self, hero):
        """
        Cause damage if the Hero is touching a spike
        """
        spike_hit_list = pygame.sprite.spritecollide(hero, self.spikes_list, False)
        if len(spike_hit_list) > 0:
            self.logger.info('hero touched spike')
            hero.damage(spike_hit_list[0].damage)

    def calc_gravity(self):
        """
        Change self.yspeed to cause an acceleration due to gravity.
        """
        if self.yspeed == 0:
            self.yspeed = self.base_y_gravity
        else:
            self.yspeed += self.gravity_acceleration

    def cause_dropped_item_gravity(self):
        """
        Cause gravity for drops and stop any dropping items/weapons from falling through the floor.
        """
        for drop in self.drops_list:
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

    def cause_ranged_attacks(self, hero):
        """
        Cause every enemy with a ranged attack to attack the hero, if within range

        :param hero: The hero to target
        """
        for e in self.enemy_list:
            distance = h.get_node_dist(hero.rect.center, e.rect.center)
            if e.is_ranged and distance <= e.attack_range:
                if e.cooldown == 0:
                    proj_list = e.ranged_attack(hero)
                    for proj in proj_list:
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
        """
        for bomb in self.bomb_list:
            hit_list = pygame.sprite.spritecollide(bomb, self.block_list, False)
            if len(hit_list) > 0:
                for block in self.block_list:
                    distance = h.get_node_dist(block.rect.center, bomb.rect.center)
                    if distance < bomb.radius and block.breakable:
                        self.logger.info('destroyed block at {0} with bomb'.format((block.rect.x, block.rect.y)))
                        self.nodes.make_passable((block.rect.centerx, block.rect.centery))
                        block.kill()

                for e in self.enemy_list:
                    distance = h.get_node_dist(e.rect.center, bomb.rect.center)
                    if distance < bomb.radius:
                        damage = hero.bomb_damage  # / distance**2  # lowers damage, but too much
                        e.damage(damage)
                        self.logger.info('damaged {0} by {1} hp with bomb'.format(e, damage))

                for drop in self.drops_list:
                    distance = h.get_node_dist(drop.rect.center, bomb.rect.center)
                    if distance < bomb.radius:
                        self.logger.info('destroyed {0} at {1} with bomb'.format(drop, (drop.rect.x, drop.rect.y)))
                        drop.kill()

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

    def setspeed(self, setx=None, sety=None):
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

    def add_weapon(self, node):
        """
        Add a random weapon to a given node
        """
        weapon = random.choice(drops.all_weapons)(node)
        self.all_sprites.add(weapon.sprite)
        self.drops_list.add(weapon.sprite)
        self.logger.debug('added weapon at {pos}'.format(pos=node))

    def add_enemy(self, enemy_, node):
        """
        Add a specific enemy to a given node
        """
        new_enemy = enemy_(self)
        new_enemy.rect.center = node
        self.enemy_list.add(new_enemy)
        self.all_sprites.add(new_enemy)
        self.logger.debug('added {enemy} at {pos}'.format(enemy=enemy_.name, pos=node))

    def add_wall(self, node, **kwargs):
        """
        add a wall with a given modifier
        """
        if 'damage' in kwargs:
            self.logger.debug('added spikes at {pos}'.format(pos=node))
        elif 'breakable' in kwargs:
            self.logger.debug('added broken wall at {pos}'.format(pos=node))
        elif 'end_timer' in kwargs:
            self.logger.debug('added wall/end_timer at {pos}'.format(pos=node))
        else:
            self.logger.debug('added wall at {pos}'.format(pos=node))

        wall = Wall(node, **kwargs)
        self.all_sprites.add(wall)

        if 'damage' not in kwargs:
            self.block_list.add(wall)
            self.nodes.add_wall(node)
        else:
            self.spikes_list.add(wall)

    def parse_room_array(self):
        """
        Turn a list of strings into an array of walls and enemies.

        Move top -> bottom through the rows, and go left -> through each character in a given row

        Add a block, enemy, chest, etc. with the characteristics below at a given position
        for each character in the room. Each block unit is 64x64 px

        KEY for room_array:
        S is stone
        P is spike
        B is a breakable wall
        T is a turret
        G is a ghost
        R is a block that stops the timer
        W is a weapon chest
        D is door <- IMPORTANT, you need a 2 wide door at the top and bottom to make the logic work
        """
        x = settings['SCREEN_RESOLUTION'][0] / 2 - 128
        y = settings['SCREEN_RESOLUTION'][1] / 2 - 128

        #Just because there are a bunch of blank tiles doesn't mean we want to spawn
        #our first real tile all the way to the right of the screen.
        #To fix this, we reduce our starting X by a tile for every blank tile we have
        blanks = [char for char in self.room_array[0] if char == '&']
        x -= 64 * len(blanks)

        xstart = x
        self.logger.info('Parsing the room into entities')
        for row in self.room_array:
            for col in row:
                node = (x+32, y+32)

                if col != "&":
                    self.nodes.append(node)

                if col == "S":
                    self.add_wall(node)

                elif col == "R":
                    self.add_wall(node, end_timer=True)

                elif col == "P":
                    self.add_wall(node, damage=1)

                elif col == "B":
                    self.add_wall(node, breakable=True)

                elif col == "V":
                    self.add_enemy(enemy.Volcano, node)

                elif col == "G":
                    self.add_enemy(enemy.Ghost, node)

                elif col == "F":
                    self.add_enemy(enemy.FireBat, node)

                elif col == "W":
                    self.add_weapon(node)

                x += 64
            y += 64
            x = xstart

        self.logger.debug('number of created enemies: {0}'.format(len(self.enemy_list)))
        self.logger.debug('number of created nodes: {0}'.format(len(self.nodes.nodes)))
        self.logger.debug('number of created weapons: {0}'.format(len(self.drops_list)))

        self.logger.info('World parsed successfully')
        self.array_parsed = True

    def add_weapons_to_world(self):
        """
        After the world is parsed into entities, add weapons to it
        """
        self.logger.debug('Adding weapons to the world')

        for node in self.nodes.nodes:
            if self.nodes.passable(node):
                if random.randint(0, 1000) <= self.weapon_factor:
                    if len(self.drops_list) == 0:
                        self.add_weapon(node)
                    else:
                        done = False
                        for existing_weapon in self.drops_list:
                            if h.get_node_dist(existing_weapon.rect.center, node) < 10000 and not done:
                                self.add_weapon(node)
                                done = True

        self.logger.debug('{0} weapons added'.format(len(self.drops_list)))