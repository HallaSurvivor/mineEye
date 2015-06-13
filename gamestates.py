"""
Store all the game states as classes that are instantiated.
"""
from math import hypot
import datetime
import pickle
import random
import pygame
from config import settings
import constants as c
import helpers as h
import rooms
import hero

pygame.init()


class GameState(object):
    """
    A superclass for all the states the game can be in.

    musicfile is a string representing the name of background music to be played.
    """

    musicfile = None

    def __init__(self):
        self.default_background = h.create_background(h.load('sand.jpg'))

    def draw(self, screen):
        """
        Will be overwritten by the subclass to draw whatever is on the screen.
        An exception will be raised when something not currently working is called
        :param screen: The pygame screen to be drawn on
        """
        raise NotImplementedError

    def update(self):
        """
        Will be overwritten by the subclass to update whatever is on the screen.
        An exception will be raised when something not currently working is called
        """
        raise NotImplementedError

    def handle_events(self, events):
        """
        Will be overwritten by the subclass to do certain things based on events.
        An exception will be raised when something not currently working is called
        :param events: A list of the events happening in a tick - obtained through
                        pygame.event.get()
        """
        raise NotImplementedError


class GameStateManager(object):
    """
    A helper class to manage game states.
    """
    def __init__(self):
        self.state = None
        self.done = False
        self.go_to(TitleScreen())

    def go_to(self, gamestate):
        """
        Change the game state to gamestate and add this class to the new gamestate's variables.

        If the new gamestate has a music file associated with it, play that music.
        """
        self.state = gamestate
        self.state.manager = self

        if gamestate.musicfile and settings['PLAY_MUSIC']:
            h.play_music(gamestate.musicfile)
        if not settings['PLAY_MUSIC']:
            pygame.mixer.music.stop()


class Menu(GameState):
    """
    A blank template for rendering menus and handling their events.
    """

    title = ""
    options = []
    descriptions = None
    selections = None

    allow_on_off = True

    def __init__(self):
        super().__init__()
        self.manager = None

        self.selected = 0
        self.list_size = len(self.options) - 1

    def draw(self, screen):
        """
        Draw the title and all the options/descriptions to the screen.
        :param screen: The pygame screen on which to draw
        """

        on = h.load_font('MelmaCracked.ttf', 16).render(
            'On', 1, c.BLACK
        )

        off = h.load_font('MelmaCracked.ttf', 16).render(
            'Off', 1, c.BLACK
        )

        screen.blit(self.default_background, (0, 0))

        rect_list = h.create_menu(screen, self.title, self.options, self.descriptions)
        if self.selections is not None:
            for index, option in enumerate(self.selections):
                if type(option) == str and self.allow_on_off:
                    if settings[option]:
                        on_rect = on.get_rect()
                        on_rect.bottomright = rect_list[index].bottomleft
                        screen.blit(on, on_rect)
                    else:
                        off_rect = off.get_rect()
                        off_rect.bottomright = rect_list[index].bottomleft
                        screen.blit(off, off_rect)

        selected_indicator = h.load('pickaxe.png')
        selected_rect = selected_indicator.get_rect()
        selected_rect.bottomleft = rect_list[self.selected].bottomright
        screen.blit(selected_indicator, selected_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == settings['DOWN'] or e.key == pygame.K_DOWN:
                    if self.selected < self.list_size:
                        self.selected += 1
                elif e.key == settings['UP'] or e.key == pygame.K_UP:
                    if self.selected > 0:
                        self.selected -= 1

                elif e.key == settings['LEFT'] or e.key == pygame.K_LEFT:
                    self.manager.go_to(TitleScreen())

                elif e.key == pygame.K_SPACE or e.key == settings['RIGHT'] or e.key == pygame.K_RIGHT:
                    if self.selections is not None:
                        if type(self.selections[self.selected]) == str:
                            if settings[self.selections[self.selected]]:
                                settings[self.selections[self.selected]] = False

                            else:
                                settings[self.selections[self.selected]] = True

                            f = open('settings', 'wb')
                            f.write(pickle.dumps(settings))
                            f.close()

                        else:
                            self.manager.go_to(self.selections[self.selected])


class TitleScreen(Menu):
    """
    The title screen game state.
    """

    musicfile = 'O_Fortuna.mp3'

    title = 'Press Space to begin!'
    options = ['Start!', 'Time Trial!', 'Settings!', 'Quit!']

    def __init__(self):
        super().__init__()

        self.selections = [ChooseHero(), ChooseHero(timer=True), ChangeSettings(), Quit()]


class ChooseHero(Menu):
    """
    A game state for choosing a hero to play as.
    """

    title = 'Choose a Hero!'
    options = [player.name for player in hero.hero_list]
    descriptions = [player.description for player in hero.hero_list]

    def __init__(self, timer=False):
        super().__init__()
        self.timer = timer

        self.selections = [InGame(timer=self.timer, chosen_hero=player) for player in hero.hero_list]


class ChangeSettings(Menu):
    """
    A game state for changing local variables like PLAY_MUSIC.
    """
    title = "Settings"
    options = ["Play Music", "Play Sound Effects", "Change Keybinds"]

    def __init__(self):
        super().__init__()
        self.selections = ['PLAY_MUSIC', 'PLAY_SFX', ChangeBinds()]


class ChangeBinds(Menu):
    """
    A place to change keybinds.
    """
    title = "KeyBinds"
    options = ["Up", "Left", "Right", "Down", "Bomb"]
    selections = [string.upper() for string in options]

    allow_on_off = False

    def __init__(self):

        super().__init__()

        self.modifying = False
        self.descriptions = [pygame.key.name(settings[option]) for option in self.selections]

    def handle_events(self, events):
        """
        Override the default event checking in order to check for any key press.
        """
        self.descriptions = [pygame.key.name(settings[option]) for option in self.selections]

        for e in events:
            if e.type == pygame.KEYDOWN:
                if not self.modifying:
                    if e.key == settings['DOWN'] or e.key == pygame.K_DOWN:
                        if self.selected < self.list_size:
                            self.selected += 1
                    elif e.key == settings['UP'] or e.key == pygame.K_UP:
                        if self.selected > 0:
                            self.selected -= 1

                    elif e.key == settings['LEFT'] or e.key == pygame.K_LEFT:
                        self.manager.go_to(TitleScreen())

                    elif e.key == pygame.K_SPACE or e.key == settings['RIGHT'] or e.key == pygame.K_RIGHT:
                        self.options[self.selected] = ">" + self.options[self.selected]
                        self.modifying = True
                else:
                    if e.key == pygame.K_ESCAPE:
                        self.options[self.selected] = self.options[self.selected][1:]
                        self.modifying = False

                    else:
                        if e.key not in [settings[selection] for selection in self.selections]:
                            settings[self.selections[self.selected]] = e.key
                            self.options[self.selected] = self.options[self.selected][1:]
                            self.modifying = False

                        else:  # If the key is already bound, pick a random key and bind it to the old option
                            for selection in self.selections:
                                if settings[selection] == e.key:
                                    found = False
                                    while not found:
                                        new_key = random.randint(10, 99)
                                        if new_key not in [settings[selection] for selection in self.selections]:
                                            found = True

                                    settings[selection] = new_key

                            settings[self.selections[self.selected]] = e.key
                            self.options[self.selected] = self.options[self.selected][1:]
                            self.modifying = False

                        f = open('settings', 'wb')
                        f.write(pickle.dumps(settings))
                        f.close()
            else:
                pass


class InGame(GameState):
    """
    A game state for moving and falling through the mine
    """

    musicfile = 'Pathetique.mp3'

    def __init__(self, timer=False, chosen_hero=hero.Demo):
        """
        Instantiate the primary Game State.
        :param timer: A boolean. True if a timer is to be displayed in the top right, False if not.
        """
        super().__init__()
        self.manager = None

        self.all_sprites_list = pygame.sprite.Group()

        self.hero = chosen_hero()

        self.start_time = datetime.datetime.now()

        self.world = None
        self.generate_world(30)
        self.hero.world = self.world

        self.timer = timer
        self.elapsed_time = 0

        self.left_pressed = False
        self.right_pressed = False

    def draw_hud(self, screen):
        """
        Draw the user Heads Up Display to the screen, includes HP, timer, Ammo, etc.
        :param screen: The screen on which to draw
        """
        # Draw the HP Bar
        hp_background = pygame.Surface(c.HP_BACKGROUND_SIZE)
        hp_background.fill(c.BLACK)
        screen.blit(hp_background, c.HP_BACKGROUND_POS)

        hp_bar = pygame.Surface((int(self.hero.hp*(c.HP_BAR_SIZE[0]/self.hero.base_hp)), int(c.HP_BAR_SIZE[1])))
        if self.hero.hp/self.hero.base_hp > .25:
            hp_bar.fill(c.BLUE)
        else:
            hp_bar.fill(c.RED)
        screen.blit(hp_bar, c.HP_BAR_POS)

        # Draw the HP text
        hp_text = h.load_font('BLKCHCRY.TTF', 32).render(
            "{0}/{1}".format(self.hero.hp, self.hero.base_hp), 1, c.WHITE
        )
        hp_text_rect = hp_text.get_rect()
        hp_text_rect.center = hp_background.get_rect().center
        screen.blit(hp_text, hp_text_rect)

        # Draw the number of bombs
        bomb_ammo = h.load_font('BLKCHCRY.TTF', 32).render(
            "Bombs: {0}".format(self.hero.bombs), 1, c.WHITE
        )
        screen.blit(bomb_ammo, c.BOMB_POS)

        # Draw the equipped weapons
        if self.hero.melee_weapon is not None:
            screen.blit(self.hero.melee_weapon.top_sprite.image, c.MELEE_POS)

        if self.hero.ranged_weapon is not None:
            screen.blit(self.hero.ranged_weapon.top_sprite.image, c.RANGED_POS)

        # Draw the timer
        if self.timer:
            if self.hero.run_timer:
                self.elapsed_time = datetime.datetime.now() - self.start_time
                formatted_elapsed_time = self.elapsed_time.total_seconds()

                elapsed_time_display = h.load_font('BLKCHCRY.TTF', 20).render(
                    "{ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, c.WHITE
                )

                time_pos = (c.TOP_RIGHT[0] - elapsed_time_display.get_rect().width - 16, 0)
                screen.blit(elapsed_time_display, time_pos)
            else:
                formatted_elapsed_time = self.elapsed_time.total_seconds()
                elapsed_time_display = h.load_font('BLKCHCRY.TTF', 48).render(
                    "Final Time: {ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, c.GREEN
                )
                elapsed_time_display_rect = elapsed_time_display.get_rect()
                elapsed_time_display_rect.center = c.CENTER
                screen.blit(elapsed_time_display, elapsed_time_display_rect)

    def draw(self, screen):
        """
        Overwrites draw in the GameState class. Draws all of the blocks and enemies in the levels in this
        game state to the screen.

        Additionally, a HUD is displayed at the top of the screen, showing:
            the Hero's HP
            the
        :param screen: The pygame screen on which to draw.
        """
        self.world.draw(screen)
        self.hero.draw(screen)
        self.draw_hud(screen)

    def update(self):
        """
        Redraw all of the blocks and enemies in their updated positions as the player interacts with the world,
        items drop, enemies move, etc.
        """
        self.world.update(self.hero)

        if self.hero.hp <= 0:
            self.manager.go_to(DeathScreen())

    def handle_events(self, events):
        """
        Parse all of the events that pygame registers inside the class.

        All of the keys are defined inside of config.py, but can be
        overwritten by the user inside of the Change Keybinds menu
        defined above as ChangeBinds()

        Pushing Keys:
            Left:
                Move to the left
            Right:
                Move to the right
            Up:
                Jump
            Down:
                Change Weapons
            Bomb:
                Throw a bomb
            Pause:
                Exit to title screen

        Clicking:
            Mouse1:
                Use Melee weapon
            Mouse2:
                Use Ranged weapon

        :param events: a list of pygame events, get via pygame.event.get()
        """

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings['LEFT']:
                    self.left_pressed = True

                    if self.hero.moving_right:
                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_right = False

                    self.world.changespeed(self.hero.actual_speed, 0)
                    self.hero.moving_left = True
                    self.hero.last_motion = 'left'

                elif event.key == settings['RIGHT']:
                    self.right_pressed = True

                    if self.hero.moving_left:
                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_left = False

                    self.world.changespeed(-self.hero.actual_speed, 0)
                    self.hero.moving_right = True
                    self.hero.last_motion = 'right'

                elif event.key == settings['UP']:
                    if not self.hero.jumping:

                        # If the hero is on a platform:
                        self.hero.rect.y += 2
                        hit_list = pygame.sprite.spritecollide(self.hero, self.world.block_list, False)
                        self.hero.rect.y -= 2
                        if len(hit_list) > 0:
                            self.world.changespeed(0, self.hero.jump_height)
                            self.hero.jumping = True
                            self.hero.start_jump = True

                    else:
                        if self.hero.can_doublejump and not self.hero.double_jumping:
                            self.world.setspeed(None, 0)
                            self.world.changespeed(0, self.hero.double_jump_height)
                            self.hero.double_jumping = True
                            self.hero.start_double_jump = True

                elif event.key == settings['BOMB']:
                    if self.hero.bombs > 0:
                        bomb = self.hero.drop_bomb()
                        self.world.bomb_list.add(bomb)
                        self.world.all_sprites.add(bomb)

                elif event.key == settings['DOWN']:
                    for drop in self.world.drops_list:
                        if drop.is_weapon:
                            if (hypot(drop.rect.centerx - c.CENTER[0], drop.rect.centery - c.CENTER[1])
                                    <= self.hero.weapon_pickup_range):
                                if drop.drop.style == 0: # Melee
                                    if self.hero.melee_weapon is not None:
                                        self.world.all_sprites.add(self.hero.melee_weapon.sprite)
                                        self.world.drops_list.add(self.hero.melee_weapon.sprite)
                                    self.hero.melee_weapon = drop.drop
                                elif drop.drop.style == 1: # Ranged
                                    if self.hero.ranged_weapon is not None:
                                        self.world.all_sprites.add(self.hero.ranged_weapon.sprite)
                                        self.world.all_sprites.add(self.hero.ranged_weapon.sprite)
                                    self.hero.ranged_weapon = drop.drop
                                drop.kill()

                elif event.key == settings['MELEE']:
                    if self.hero.melee_weapon is not None:
                        for e in self.world.enemy_list:
                            dist = hypot(e.rect.centerx - c.CENTER[0], e.rect.centery - c.CENTER[1])
                            if dist <= 500:
                                print(dist)
                            if dist <= self.hero.melee_weapon.range:
                                e.damage(self.hero.melee_weapon.power)

                elif event.key == settings['RANGED']:
                    pass

                # Quit to TitleScreen (eventually pause menu) if the user presses escape
                elif event.key == settings['PAUSE']:
                    self.manager.go_to(TitleScreen())

            elif event.type == pygame.KEYUP:
                # Cancel the motion by adding the opposite of the keydown situation
                if event.key == settings['LEFT']:
                    self.left_pressed = False

                    if self.hero.moving_left:
                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_left = False

                    if self.right_pressed and not self.hero.moving_right:
                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_right = True
                        self.hero.last_motion = 'right'

                elif event.key == settings['RIGHT']:
                    self.right_pressed = False

                    if self.hero.moving_right:
                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_right = False

                    if self.left_pressed and not self.hero.moving_left:
                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_left = True
                        self.hero.last_motion = 'left'

                elif event.key == settings['UP']:
                    pass

                elif event.key == settings['DOWN']:
                    pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.hero.melee_weapon is not None:
                        for e in self.world.enemy_list:
                            dist = hypot(e.rect.centerx - c.CENTER[0], e.rect.centery - c.CENTER[1])
                            if dist <= 500:
                                print(dist)
                            if dist <= self.hero.melee_weapon.range:
                                e.damage(self.hero.melee_weapon.power)
                elif event.button == 3:
                    pass
            else:
                pass

    def die(self):
        self.manager.go_to(DeathScreen())

    def generate_world(self, n):
        """
        Generate the world by randomly selecting n rooms.
        :param n: The Int number of rooms to randomly choose
        """
        room_list = []
        possible_rooms = dict([(k, v) for k, v in rooms.room_dict.items() if k not in
                              ["StartingRoom", "EndingRoom"]])

        room_list.append(rooms.room_dict["StartingRoom"])

        move_down_counter = 0
        move_left_counter = 0
        move_right_counter = 0

        total_displacement = 0

        for i in range(n):
            matched = False
            while not matched:
                possible_next_room = random.choice(list(possible_rooms.values()))

                if possible_next_room[0] == rooms.MoveDown:
                    if move_down_counter <= 3:
                        room_list.append(possible_next_room)

                        move_down_counter += 1
                        move_left_counter = 0
                        move_right_counter = 0
                        matched = True

                elif possible_next_room[0] == rooms.MoveLeft:
                    # Solves a bug with rendering left of the start
                    if total_displacement >= 2*len(possible_next_room[-1]):
                        if move_left_counter <= 5:
                            room_list.append(possible_next_room)

                            move_down_counter = 0
                            move_left_counter += 1
                            move_right_counter = 0

                            total_displacement -= len(possible_next_room[-1])
                            matched = True

                elif possible_next_room[0] == rooms.MoveRight:
                    if move_right_counter <= 5:
                        room_list.append(possible_next_room)

                        move_down_counter = 0
                        move_left_counter = 0
                        move_right_counter += 1

                        total_displacement += len(possible_next_room[-1])
                        matched = True

        room_list.append(rooms.room_dict["EndingRoom"])

        self.world = rooms.World(room_list)


class DeathScreen(GameState):
    """
    A game state for showing the hero's death.
    """

    musicfile = 'Raven.mp3'

    def __init__(self):
        super().__init__()
        self.manager = None

    def draw(self, screen):
        screen.fill(c.BLACK)
        death_text = h.load_font("Melma.ttf", 32).render(
            "You Died! \n Press any key to try again.", 1, c.RED
        )
        death_text_x = death_text.get_rect().width / 2
        death_text_y = death_text.get_rect().height / 2
        centered_pos = (c.CENTER[0] - death_text_x, c.CENTER[1] - death_text_y)

        screen.blit(death_text, centered_pos)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.manager.go_to(TitleScreen())


class Quit(GameState):
    """
    A gamestate to quit. Done to make things more general.
    """

    def __init__(self):
        super().__init__()
        self.manager = None

    def draw(self, screen):
        self.manager.done = True

    def update(self):
        pass