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

try:
    f = open('seeds', 'rb')
    seeds = pickle.loads(f.read())
    f.close()
except FileNotFoundError:
    seeds = [''] * 10
    f = open('seeds', 'wb')
    f.write(pickle.dumps(seeds))
    f.close()


class GameState(object):
    """
    A superclass for all the states the game can be in.

    musicfile is a string representing the name of background music to be played.
    """

    musicfile = None
    background_tile = 'sand.jpg'

    def __init__(self):
        self.default_background = h.create_background(h.load(self.background_tile))

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
        self.previous_state = None

    def go_to(self, gamestate):
        """
        Change the game state to gamestate and add this class to the new gamestate's variables.

        If the new gamestate has a music file associated with it, play that music.
        """
        if type(gamestate) is not TitleScreen:
            self.previous_state = self.state
        else:
            self.previous_state = None

        self.state = gamestate
        self.state.manager = self

        if gamestate.musicfile and settings['PLAY_MUSIC']:
            h.play_music(gamestate.musicfile)
        if not settings['PLAY_MUSIC']:
            pygame.mixer.music.stop()

    def go_back(self):
        """
        Return to the previous gamestate to fix an infinite recursion bug with menus.
        """
        if self.previous_state is not None:
            self.state = self.previous_state
        else:
            self.go_to(TitleScreen())
        self.previous_state = None


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
        if self.default_background.get_size() != screen.get_size():
            self.default_background = h.create_background(h.load(self.background_tile))

        screen.blit(self.default_background, (0, 0))

        rect_list = h.create_menu(screen, self.title, self.options, self.descriptions)
        if self.selections is not None:
            for index, option in enumerate(self.selections):
                if type(option) == str and self.allow_on_off and option != 'go back':
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
                # Moving the Selection Cursor
                if e.key == settings['DOWN'] or e.key == pygame.K_DOWN:
                    if self.selected < self.list_size:
                        self.selected += 1
                elif e.key == settings['UP'] or e.key == pygame.K_UP:
                    if self.selected > 0:
                        self.selected -= 1

                # Going back a screen
                elif e.key == settings['LEFT'] or e.key == pygame.K_LEFT:
                    self.manager.go_back()

                # Selecting an option
                elif e.key == pygame.K_SPACE or e.key == settings['RIGHT'] or \
                            e.key == pygame.K_RIGHT or e.key == pygame.K_RETURN:
                    if self.selections is not None:
                        if type(self.selections[self.selected]) == str:
                            # if it's a back button
                            if self.selections[self.selected] == 'go back':
                                self.manager.go_back()

                            # if it's a settings modifier
                            else:
                                if settings[self.selections[self.selected]]:
                                    settings[self.selections[self.selected]] = False

                                else:
                                    settings[self.selections[self.selected]] = True

                                f = open('settings', 'wb')
                                f.write(pickle.dumps(settings))
                                f.close()
                        elif type(self.selections[self.selected]) == tuple:
                            # if it's a screen resolution
                            settings['SCREEN_RESOLUTION'] = self.selections[self.selected]
                            settings['WIDTH'] = self.selections[self.selected][0]
                            settings['HEIGHT'] = self.selections[self.selected][1]

                            f = open('settings', 'wb')
                            f.write(pickle.dumps(settings))
                            f.close()
                        else:
                            self.manager.go_to(self.selections[self.selected])

                if self.title == 'Custom Seeded Maps' and e.key == pygame.K_BACKSPACE:
                    self.manager.go_to(AddSeed(self.selected))


class TitleScreen(Menu):
    """
    The title screen game state.
    """

    musicfile = 'O_Fortuna.mp3'

    title = 'Press Space to begin!'
    options = ['Start!', 'My Maps', 'Settings!', 'Quit!']

    def __init__(self):
        super().__init__()
        self.selections = [ChooseHero(timer=True), PlayerMaps(), ChangeSettings(), Quit()]


class PlayerMaps(Menu):
    """
    A place for the player to store maps based on certain seeds. (page 1)

    This helps with speed running by allowing the user to save/add
    certain "good" maps to more directly compare skill to other players.
    """
    title = 'Custom Seeded Maps'
    descriptions = ['', '', '', '', '', 'use backspace to change an existing seed']
    options = ['EMPTY'] * 5
    options.append('NEXT PAGE')

    def __init__(self):
        super().__init__()
        self.options = ['EMPTY'] * 5
        self.options.append('NEXT PAGE')
        for index, seed in enumerate(seeds):
            if index < 5:
                if seed != '':
                    self.options[index] = seed

        self.selections = []
        for index, option in enumerate(self.options):
            if option == 'EMPTY':
                self.selections.append(AddSeed(index))
            elif option == 'NEXT PAGE':
                self.selections.append(PlayerMaps2())
            else:
                self.selections.append(ChooseHero(timer=True, seed=option))


class PlayerMaps2(Menu):
    """
    A place for the player to store maps based on certain seeds. (page 2)

    This helps with speed running by allowing the user to save/add
    certain "good" maps to more directly compare skill to other players.
    """
    title = 'Custom Seeded Maps'
    descriptions = ['', '', '', '', '', 'use backspace to change an existing seed']
    options = ['EMPTY'] * 5
    options.append('LAST PAGE')

    def __init__(self):
        super().__init__()
        self.options = ['EMPTY'] * 5
        self.options.append('LAST PAGE')
        for index, seed in enumerate(seeds):
            if index > 4:
                if seed != '':
                    self.options[index - 5] = seed

        self.selections = []
        for index, option in enumerate(self.options):
            if option == 'EMPTY':
                self.selections.append(AddSeed(index + 5))
            elif option == 'LAST PAGE':
                self.selections.append('go back')
            else:
                self.selections.append(ChooseHero(timer=True, seed=option))


class AddSeed(Menu):
    """
    Provide a means of adding/changing a seed to use to spawn a world.
    """
    title = 'Add Custom Seeds'
    options = ['Push Space To Edit Seed:', 'Save']

    def __init__(self, index):
        super().__init__()
        self.modifying = False
        self.index = index
        self.seed = str(seeds[self.index])
        self.descriptions = [self.seed, ""]

    def handle_events(self, events):
        """
        Override the default event checking in order to check for any key press.
        """
        self.descriptions = [self.seed, ""]
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
                        self.manager.go_back()

                    elif e.key == pygame.K_SPACE or e.key == settings['RIGHT'] or e.key == pygame.K_RIGHT:
                        if self.selected == 0:
                            self.options[self.selected] = ">" + self.options[self.selected] + "<"
                            self.modifying = True
                        else:
                            global seeds
                            seeds[self.index] = self.seed
                            f = open('seeds', 'wb')
                            f.write(pickle.dumps(seeds))
                            f.close()
                            self.manager.go_to(PlayerMaps())

                else:
                    if e.key == pygame.K_ESCAPE or e.key == pygame.K_SPACE or e.key == pygame.K_RETURN:
                        self.modifying = False
                        self.options[self.selected] = self.options[self.selected][1:-1]

                    elif e.key == pygame.K_BACKSPACE:
                        self.seed = self.seed[:-1]

                    else:
                        if e.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3,
                                     pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                                     pygame.K_8, pygame.K_9]:
                            self.seed += pygame.key.name(e.key)
            else:
                pass


class ChooseHero(Menu):
    """
    A game state for choosing a hero to play as.
    """

    title = 'Choose a Hero!'
    options = [player.name for player in hero.hero_list]
    descriptions = [player.description for player in hero.hero_list]

    def __init__(self, timer=False, seed=None):
        super().__init__()
        self.timer = timer
        self.seed = seed
        self.selections = [InGame(timer=self.timer, chosen_hero=player, seed=self.seed) for player in hero.hero_list]


class ChangeSettings(Menu):
    """
    A game state for changing local variables like PLAY_MUSIC.
    """
    title = "Settings"
    options = ["Play Music", "Play Sound Effects", "Change Keybinds", "Change Aspect Ratio"]

    def __init__(self):
        super().__init__()
        self.selections = ['PLAY_MUSIC', 'PLAY_SFX', ChangeBinds(), ChangeRatio()]


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

        valid_options = [
            # letters
            pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g,
            pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n,
            pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u,
            pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z,
            # numpad
            pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5,
            pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9, pygame.K_KP_ENTER,
            pygame.K_KP_DIVIDE, pygame.K_KP_EQUALS, pygame.K_KP_MINUS, pygame.K_KP_MULTIPLY,
            pygame.K_KP_PERIOD, pygame.K_KP_PLUS,
            # misc
            pygame.K_SEMICOLON, pygame.K_COMMA, pygame.K_PERIOD, pygame.K_SLASH, pygame.K_SPACE,
            pygame.K_MINUS, pygame.K_EQUALS, pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET,
            pygame.K_BACKSLASH, pygame.K_QUOTE,
            # numbers
            pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
            pygame.K_7, pygame.K_8, pygame.K_9

        ]

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
                        self.manager.go_back()
                    elif e.key == pygame.K_SPACE or e.key == settings['RIGHT'] or \
                            e.key == pygame.K_RIGHT or e.key == pygame.K_RETURN:
                        self.options[self.selected] = ">" + self.options[self.selected] + "<"
                        self.modifying = True

                else:  # If we are modifying a bind
                    if e.key == pygame.K_ESCAPE or e.key == pygame.K_RETURN or e.key == pygame.K_LEFT:
                        self.options[self.selected] = self.options[self.selected][1:-1]
                        self.modifying = False

                    else:
                        if e.key in valid_options:
                            # If the key is not already bound
                            if e.key not in [settings[selection] for selection in self.selections]:
                                settings[self.selections[self.selected]] = e.key

                            else:  # If the key is already bound, pick a random key and bind it to the old option
                                for selection in self.selections:
                                    if settings[selection] == e.key:
                                        # Get a list of all the unbound, legal, keys
                                        unbound = [key for key in valid_options if key not in
                                                   [settings[selection] for selection in self.selections]]

                                        new_key = random.choice(unbound)
                                        settings[selection] = new_key

                                settings[self.selections[self.selected]] = e.key

                            self.options[self.selected] = self.options[self.selected][1:-1]
                            self.modifying = False

                            f = open('settings', 'wb')
                            f.write(pickle.dumps(settings))
                            f.close()
            else:
                pass


class ChangeRatio(Menu):
    title = "Change Aspect Ratio"
    options = ["16:9", "4:3"]

    def __init__(self):
        super().__init__()
        self.selections = [(1600, 900), (640, 480)]


class InGame(GameState):
    """
    A game state for moving and falling through the mine.

    Drawn:
        Draw the World - enemies, blocks, particles, drops
        Draw the Hero - always centered
        Draw the HUD - Timer, HP, Ammo, etc.
    Events:
        Check the mvt keys (defined in settings dict)
        Check the mouse position/mouse buttons
        Check for clicking
    Create the World:
        Semi-Randomly create the world based on a seed
        and the criteria that prevents generation bugs
        and keeps the game interesting, i.e. no more than
        3 right moving rooms in a row.
    """

    musicfile = 'Pathetique.mp3'

    def __init__(self, timer=False, chosen_hero=hero.Demo, seed=None):
        """
        Instantiate the primary Game State.

        :param timer: A boolean. True if a timer is to be displayed in the top right, False if not.
        :param seed: The seed to use to generate the world.
        """
        super().__init__()
        self.manager = None

        if seed is None:
            self.seed = random.random()
        else:
            self.seed = seed

        random.seed(self.seed)

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

        If the timer ends, go to WinScreen.
        :param screen: The screen on which to draw
        """
        # Draw the HP Bar
        hp_background = pygame.Surface((int(c.HP_BAR_WIDTH*settings['WIDTH']), int(c.HP_BAR_HEIGHT*settings['HEIGHT'])))
        hp_background.fill(c.BLACK)
        hp_background_rect = hp_background.get_rect()
        hp_background_rect.x = 2
        hp_background_rect.y = 2
        screen.blit(hp_background, hp_background_rect)

        hp_bar = pygame.Surface(
            (int((c.HP_BAR_WIDTH*settings['WIDTH'] - 4) * self.hero.hp/self.hero.base_hp),
             int(c.HP_BAR_HEIGHT*settings['HEIGHT'] - 4)
            )
        )

        if self.hero.hp/self.hero.base_hp > .25:
            hp_bar.fill(c.BLUE)
        else:
            hp_bar.fill(c.RED)

        hp_bar_rect = hp_bar.get_rect()
        hp_bar_rect.centery = hp_background_rect.centery
        hp_bar_rect.left = hp_background_rect.left + 2

        screen.blit(hp_bar, hp_bar_rect)

        # Draw the HP text
        hp_text = h.load_font('BLKCHCRY.TTF', 32).render(
            "{0}/{1}".format(self.hero.hp, self.hero.base_hp), 1, c.WHITE
        )
        hp_text_rect = hp_text.get_rect()
        hp_text_rect.center = hp_background_rect.center
        screen.blit(hp_text, hp_text_rect)

        # Draw the number of bombs
        bomb_ammo = h.load_font('BLKCHCRY.TTF', 32).render(
            "Bombs: {0}".format(self.hero.bombs), 1, c.WHITE
        )
        screen.blit(bomb_ammo, (c.BOMB_POS_X*settings['WIDTH'], c.BOMB_POS_Y*settings['HEIGHT']))

        # Draw the equipped weapons
        if self.hero.melee_weapon is not None:
            screen.blit(self.hero.melee_weapon.top_sprite.image,
                        (c.MELEE_POS_X*settings['WIDTH'], c.MELEE_POS_Y*settings['HEIGHT']))

        if self.hero.ranged_weapon is not None:
            screen.blit(self.hero.ranged_weapon.top_sprite.image,
                        (c.RANGED_POS_X*settings['WIDTH'], c.RANGED_POS_Y*settings['HEIGHT']))

        # Draw the timer
        if self.hero.run_timer:
            if self.timer:
                self.elapsed_time = datetime.datetime.now() - self.start_time
                formatted_elapsed_time = self.elapsed_time.total_seconds()

                elapsed_time_display = h.load_font('BLKCHCRY.TTF', 20).render(
                    "{ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, c.WHITE
                )

                elapsed_rect = elapsed_time_display.get_rect()
                elapsed_rect.top = 0
                elapsed_rect.right = settings['WIDTH']
                screen.blit(elapsed_time_display, elapsed_rect)
        else:
            self.manager.go_to(WinScreen(self.seed, self.elapsed_time))

    def draw(self, screen):
        """
        Overwrites draw in the GameState class. Draws all of the blocks and enemies in the levels in this
        game state to the screen.

        Additionally, a HUD is displayed at the top of the screen.
        :param screen: The pygame screen on which to draw.
        """
        self.world.draw(screen)
        self.hero.draw(screen)
        self.draw_hud(screen)

    def update(self):
        """
        Recalculate the positions of everything in the world.

        Additionally, check the Hero's health
        """
        self.world.update(self.hero)
        self.hero.update()

        if self.hero.hp <= 0:
            self.die()

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
                            if hypot(drop.rect.centerx - self.hero.rect.centerx,
                                     drop.rect.centery - self.hero.rect.centery) <= self.hero.weapon_pickup_range:

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

                # Quit to TitleScreen (eventually pause menu) if the user presses escape
                elif event.key == settings['PAUSE']:
                    if settings['DEBUG']:
                        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                            settings['GOD MODE'] = True
                        else:
                            self.manager.go_to(TitleScreen())
                    else:
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
                if event.button == 1:  # Left Click
                    if self.hero.melee_weapon is not None:
                        for e in self.world.enemy_list:
                            dist = hypot(e.rect.centerx - self.hero.rect.centerx,
                                         e.rect.centery - self.hero.rect.centery)
                            if dist <= self.hero.melee_weapon.range:
                                e.damage(self.hero.melee_weapon.power * self.hero.actual_damage_multiplier)
                elif event.button == 3:  # Right Click
                    pass
            else:
                pass

    def die(self):
        self.manager.go_to(DeathScreen(self.seed))

    def generate_world(self, n):
        """
        Generate the world by semi-randomly selecting n rooms.

        Creates a list of rooms that gets turned into a list of strings inside
        rooms.Room.parse_room_array()
        From there, each character in the list of strings is turned into its
        appropriate block.

        * Make an empty list - room_list
        * Make a list of the rooms to choose from (not StartingRoom and EndingRoom)
        * Add StartingRoom to the beginning
        * Create counters to remember how often we move to the right/left/down
        * Create a total_displacement counter to prevent a bug
            The bug is caused by having a net negative displacement,
            i.e. the room need to generate blocks to the left of the leftmost
            block in StartingRoom.
            To mitigate this, total_displacement counts the number of blocks to the right
            the current door is, and then compares it to how far left the room needs to
            render itself. If the room needs to render too far to the left, a new room is
            chosen
        * Iterate n times through the list of possible rooms
        * Using the game seed, randomly select a room on each pass
        * If the selected room matches the selection criteria, add it to the list,
        otherwise, try again with a different room.
            * Criteria are as follows:
                * Don't move in the same direction more than 5 times
                * Don't move down more than 3 times
                * Total Displacement must be more than twice the length of a left-moving room
                    (the factor of two is for complete certainty)
        * Finally, add the ending room

        :param n: The Int number of rooms to randomly choose
        """

        room_list = []
        possible_rooms = [v for k, v in sorted(rooms.room_dict.items()) if k not in ["StartingRoom", "EndingRoom"]]

        room_list.append(rooms.room_dict["StartingRoom"])

        move_down_counter = 0
        move_left_counter = 0
        move_right_counter = 0

        total_displacement = 0
        for i in range(n):
            matched = False
            while not matched:
                possible_next_room = random.choice(possible_rooms)

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

        self.world = rooms.World(room_list, self.seed)


class DeathScreen(GameState):
    """
    A game state for showing the hero's death.

    Returns to title screen when any button is pressed,
    Show "you lose" text alongside the seed of the world
    that was played.
    """

    musicfile = 'Raven.mp3'

    def __init__(self, seed):
        super().__init__()
        self.manager = None
        self.seed = seed

    def draw(self, screen):
        screen.fill(c.BLACK)
        death_text = h.load_font("Melma.ttf", 32).render(
            "You Died! \n Press any key to try again.", 1, c.RED
        )
        death_text_x = death_text.get_rect().width / 2
        death_text_y = death_text.get_rect().height / 2
        centered_pos = (settings['WIDTH']/2 - death_text_x, settings['HEIGHT']/2 - death_text_y)

        screen.blit(death_text, centered_pos)

        seed_text = h.load_font("Melma.ttf", 16).render(
            "SEED: {0}".format(self.seed), 1, c.BLUE
        )
        seed_rect = seed_text.get_rect()
        seed_rect.right = settings['WIDTH']
        seed_rect.bottom = settings['HEIGHT']
        screen.blit(seed_text, seed_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.manager.go_to(TitleScreen())


class WinScreen(GameState):
    """
    A gamestate for showing a victory.

    Returns to title screen when any button is pressed,
    Show "you win" text alongside the seed of the world
    that was played.
    """

    def __init__(self, seed, elapsed_time):
        super().__init__()
        self.manager = None
        self.seed = seed
        self.elapsed_time = elapsed_time

    def draw(self, screen):
        screen.fill(c.BLACK)
        # Print the "YOU WIN!" text
        win_text = h.load_font("Melma.ttf", 32).render(
            "You Win! \n Press any key to try again.", 1, c.GREEN
        )
        centered_pos = win_text.get_rect()
        centered_pos.center = (settings['WIDTH']/2, settings['HEIGHT']/2)
        screen.blit(win_text, centered_pos)

        # Print the final time
        formatted_elapsed_time = self.elapsed_time.total_seconds()
        elapsed_time_display = h.load_font('BLKCHCRY.TTF', 48).render(
            "Final Time: {ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, c.GREEN
        )
        elapsed_time_display_rect = elapsed_time_display.get_rect()
        elapsed_time_display_rect.center = (settings['WIDTH']/2, settings['HEIGHT']/2)
        elapsed_time_display_rect.y += .15*settings['HEIGHT']
        screen.blit(elapsed_time_display, elapsed_time_display_rect)

        # Print the seed
        seed_text = h.load_font("Melma.ttf", 16).render(
            "SEED: {0}".format(self.seed), 1, c.BLUE
        )
        seed_rect = seed_text.get_rect()
        seed_rect.right = settings['WIDTH']
        seed_rect.bottom = settings['HEIGHT']
        screen.blit(seed_text, seed_rect)

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