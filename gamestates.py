"""
Store all the GameStates as classes that are instantiated.

GameStates exist as classes that are drawn to the screen and updated.
    Each GameState has three methods, draw, update, handle_events.

    draw is called in run.py and draws everything in the game state

    update is called in run.py immediately before draw, and changes the positions
    of objects on screen based on user input, enemy motion algorithms, etc.

    handle_events is called in run.py and is passed a list of all the pygame
    events that occur. Depending on the event that occurs, i.e. pushing the W
    key, a different change happens in the game.

GameState is subclassed by Menu, which automatically creates a menu of items

the GameState is changed via GameStateManager.
    The GameStateManager has two methods, go_to and go_back.

    go_to takes an instance of a GameState, and sets that to be the
    active GameState - the one drawn and updated in run.py

    go_back simply returns to the previous GameState.
"""
import os
from math import hypot
import logging
import pickle
import random
import pygame
from config import settings
import constants as c
import helpers as h
import rooms
import hero

module_logger = logging.getLogger('mineEye.gamestates')

try:
    module_logger.debug('Try to load seeds')
    f = open('seeds', 'rb')
    seeds = pickle.loads(f.read())
    f.close()
except FileNotFoundError:
    module_logger.debug('Failed - creating seeds instead')
    seeds = [''] * 11
    f = open('seeds', 'wb')
    f.write(pickle.dumps(seeds))
    f.close()


class GameState:
    """
    A superclass for all the states the game can be in.

    musicfile is a string representing the name of background music to be played.
    """

    musicfile = None
    background_tile = 'menubg.png'

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


class GameStateManager:
    """
    A helper class to manage game states.
    """
    def __init__(self):
        self.state = None
        self.done = False
        self.go_to(TitleScreen())
        self.previous_state = None
        self.logger = logging.getLogger('mineEye.gamestates.GameStateManager')

    def go_to(self, gamestate):
        """
        Change the game state to gamestate and add this class to the new gamestate's variables.

        If the new gamestate has a music file associated with it, play that music.
        """
        if type(gamestate) is not TitleScreen and type(self.state) is not AddSeed:
            self.previous_state = self.state
        else:
            self.previous_state = None

        if type(gamestate) is InGame:
            self.logger.info('==Enter Game==')
            self.logger.info('SEED: {0}'.format(gamestate.seed))
            self.logger.info('HERO: {0}'.format(gamestate.hero))
            gamestate.enter_world()

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

    show_back_button = True

    def __init__(self):
        super().__init__()
        self.manager = None

        self.logger = logging.getLogger('mineEye.gamestates.Menu')

        self.selected = 0
        self.list_size = len(self.options) - 1

        self.rect_list = []

    def extra_draw(self, screen):
        """
        A blank draw method called in the main draw function.

        Meant to be overwritten to draw menu specific items without
        overwriting the entire draw method.
        :param screen: The screen on which to draw
        """

        pass

    def draw(self, screen):
        """
        Draw the title and all the options/descriptions to the screen.
        :param screen: The pygame screen on which to draw
        """
        on = h.load_font('melma.ttf', 16).render(
            'On', 1, c.BLACK
        )

        off = h.load_font('melma.ttf', 16).render(
            'Off', 1, c.BLACK
        )
        if self.default_background.get_size() != screen.get_size():
            self.default_background = h.create_background(h.load(self.background_tile))
        screen.blit(self.default_background, (0, 0))

        if not self.rect_list:
            self.rect_list = h.create_menu(screen, self.title, self.options, self.descriptions)
        else:
            h.create_menu(screen, self.title, self.options, self.descriptions)
        if self.selections is not None:
            for index, option in enumerate(self.selections):
                if type(option) == str and option != 'go back' and option[:5] != 'seed:':
                    if settings[option]:
                        on_rect = on.get_rect()
                        on_rect.bottomright = self.rect_list[index].bottomleft
                        screen.blit(on, on_rect)
                    else:
                        off_rect = off.get_rect()
                        off_rect.bottomright = self.rect_list[index].bottomleft
                        screen.blit(off, off_rect)

        selected_indicator = h.load('pickaxe.png')
        selected_rect = selected_indicator.get_rect()
        selected_rect.bottomleft = self.rect_list[self.selected].bottomright
        screen.blit(selected_indicator, selected_rect)

        if self.show_back_button:
            back_button = h.load_font('melma.ttf', 20).render(
                'Back', 1, c.BLACK
            )
            back_rect = back_button.get_rect()
            back_rect.bottomleft = (0, settings['HEIGHT'])
            if back_rect not in self.rect_list:
                self.rect_list.append(back_rect)
                self.list_size += 1

                self.selections.append('go back')
            screen.blit(back_button, back_rect)

        self.extra_draw(screen)

        cursor = h.load('cursor.png')
        cursor_rect = cursor.get_rect()
        cursor_rect.center = pygame.mouse.get_pos()
        screen.blit(cursor, cursor_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            self.handle_keyboard(event)
            self.handle_mouse(event)

    def select_option(self):
        """
        Activate the currently highlighted option.
        """
        global seeds

        if self.selections is not None:
            if type(self.selections[self.selected]) == str:
                # if it's a back button
                if self.selections[self.selected] == 'go back':
                    self.manager.go_back()

                # if it's an add-this-seed
                elif self.selections[self.selected][:5] == 'seed:':
                    found = False
                    for index, seed in enumerate(seeds):
                        if seed == '' and not found:
                            seeds[index] = self.selections[self.selected][5:]
                            self.logger.info('added seed {0} from win/death menu'.format(self.selections[self.selected][5:]))
                            f = open('seeds', 'wb')
                            f.write(pickle.dumps(seeds))
                            f.close()
                            found = True
                    else:
                        if not found:
                            self.logger.INFO('Tried to add seed {0}, but there were no available slots'.format(self.selections[self.selected][5:]))

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

    def handle_mouse(self, event):
        """
        Handle all the clicking and mouse motion events.

        :param event: A single event from the list.
        """

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for index, rect in enumerate(self.rect_list):
                if rect.collidepoint(pos):
                    self.selected = index

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for index, rect in enumerate(self.rect_list):
                if rect.collidepoint(pos):
                    self.select_option()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.title == 'Custom Seeded Maps':
                self.manager.go_to(AddSeed(self.selected))

    def handle_keyboard(self, event):
        """
        Handle all of the keyboard inputs.

        :param event: An event from the pygame event list
        """
        if event.type == pygame.KEYDOWN:
            # Moving the Selection Cursor
            if event.key == settings['DOWN'] or event.key == pygame.K_DOWN:
                if self.selected < self.list_size:
                    self.selected += 1
            elif event.key == settings['UP'] or event.key == pygame.K_UP:
                if self.selected > 0:
                    self.selected -= 1

            # Going back a screen
            elif event.key == settings['LEFT'] or event.key == pygame.K_LEFT:
                self.manager.go_back()

            # Selecting an option
            elif event.key == pygame.K_SPACE or event.key == settings['RIGHT'] or \
                        event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
                self.select_option()

            if self.title == 'Custom Seeded Maps' and event.key == pygame.K_BACKSPACE:
                self.manager.go_to(AddSeed(self.selected))


class TitleScreen(Menu):
    """
    The title screen game state.
    """

    musicfile = 'O_Fortuna.mp3'

    title = 'Press Space to begin!'
    options = ['Start!', 'My Maps', 'Settings!', 'Quit!']

    show_back_button = False

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
    descriptions = ['', '', '', '', '', 'right click or use backspace to change an existing seed']
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
    descriptions = ['', '', '', '', '', 'right click or use backspace to change an existing seed']
    options = ['EMPTY'] * 5
    options.append('LAST PAGE')

    def __init__(self):
        super().__init__()
        self.options = ['EMPTY'] * 6
        for index, seed in enumerate(seeds):
            if index > 4:
                if seed != '':
                    self.options[index - 5] = seed

        self.selections = []
        for index, option in enumerate(self.options):
            if option == 'EMPTY':
                self.selections.append(AddSeed(index + 5))
            else:
                self.selections.append(ChooseHero(timer=True, seed=option))


class AddSeed(Menu):
    """
    Provide a means of adding/changing a seed to use to spawn a world.
    """
    title = 'Add Custom Seeds'
    options = ['Edit Seed:', 'Save']

    show_back_button = False

    def __init__(self, index):
        super().__init__()
        self.modifying = False
        self.index = index
        self.seed = str(seeds[self.index])
        self.descriptions = [self.seed, ""]

    def select_option(self):
        """
        Overwrite the basic selection feature to enable seed modification and saving.
        """
        if self.selected == 0 and not self.modifying:
            self.options[self.selected] = ">" + self.options[self.selected] + "<"
            self.modifying = True
        else:
            global seeds
            if self.options[0][0] == ">":
                self.options[0] = self.options[0][1:-1]

            seeds[self.index] = self.seed
            f = open('seeds', 'wb')
            f.write(pickle.dumps(seeds))
            f.close()
            self.manager.go_to(PlayerMaps())

    def handle_keyboard(self, event):
        """
        Override the default event checking in order to check for any key press.
        """
        self.descriptions = [self.seed, ""]
        if event.type == pygame.KEYDOWN:
            if not self.modifying:
                if event.key == settings['DOWN'] or event.key == pygame.K_DOWN:
                    if self.selected < self.list_size:
                        self.selected += 1
                elif event.key == settings['UP'] or event.key == pygame.K_UP:
                    if self.selected > 0:
                        self.selected -= 1

                elif event.key == settings['LEFT'] or event.key == pygame.K_LEFT:
                    self.manager.go_back()

                elif event.key == pygame.K_SPACE or event.key == settings['RIGHT'] or event.key == pygame.K_RIGHT:
                    self.select_option()

            else:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.modifying = False
                    self.options[self.selected] = self.options[self.selected][1:-1]

                elif event.key == pygame.K_BACKSPACE:
                    self.seed = self.seed[:-1]

                else:
                    if event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3,
                                 pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                                 pygame.K_8, pygame.K_9]:
                        self.seed += pygame.key.name(event.key)
        else:
            pass


class ChooseHero(Menu):
    """
    A game state for choosing a hero to play as.
    """

    title = 'Choose a Hero!'
    options = [player.name for player in hero.hero_list]
    descriptions = [player.description for player in hero.hero_list]

    def __init__(self, timer=True, seed=None):
        super().__init__()

        self.logger = logging.getLogger('mineEye.gamestates.ChooseHero')

        self.timer = timer
        if seed is None:
            self.seed = random.randint(0, 1000000000)
            self.logger.info('Random Seed: {0}'.format(self.seed))
        else:
            self.seed = int(seed)
            self.logger.info('PreSelected Seed: {0}'.format(self.seed))

        self.selections = [InGame(timer=self.timer, chosen_hero=player, seed=self.seed) for player in hero.hero_list]


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
        self.descriptions = [pygame.key.name(settings[option]) for option in self.selections if option != 'go back']

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

    def __init__(self, seed, timer=False, chosen_hero=hero.Demo):
        """
        Instantiate the primary Game State.

        :param timer: A boolean. True if a timer is to be displayed in the top right, False if not.
        :param seed: The seed to use to generate the world.
        :param chosen_hero: The hero who will enter the world.
        """

        super().__init__()

        self.logger = logging.getLogger('mineEye.gamestates.InGame')

        self.manager = None

        self.seed = seed

        self.tick_count = 0

        self.all_sprites_list = pygame.sprite.Group()
        self.hero = chosen_hero()

        self.world = None

        self.timer = timer
        self.elapsed_time = 0

        self.left_pressed = False
        self.right_pressed = False

    def enter_world(self):
        """
        Create the world, and give the world to the Hero.

        Avoids generating the world multiple times due to
        multiple instances of GameState existing at once.
        """
        self.logger.info('--====NEW WORLD====--')
        self.create_world(30)
        self.hero.world = self.world

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
        hp_text = h.load_font('luximb.ttf', 32).render(
            "{0}/{1}".format(self.hero.hp, self.hero.base_hp), 1, c.WHITE
        )
        hp_text_rect = hp_text.get_rect()
        hp_text_rect.center = hp_background_rect.center
        screen.blit(hp_text, hp_text_rect)

        # Draw the number of bombs
        bomb_ammo = h.load_font('luximb.ttf', 32).render(
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
                self.elapsed_time += 1
                partials = self.elapsed_time % 60
                seconds = ((self.elapsed_time - partials) // 60) % 60
                minutes = (((self.elapsed_time - partials) // 60) - seconds) // 60
                if len(str(partials)) != 2:
                    partials = "0" + str(partials)
                if len(str(seconds)) != 2:
                    seconds = "0" + str(seconds)
                if len(str(minutes)) != 2:
                    minutes = "0" + str(minutes)
                formatted_elapsed_time = "{minutes}:{seconds}:{partials}".format(minutes=minutes, seconds=seconds, partials=partials)

                elapsed_time_display = h.load_font('luximb.ttf', 32).render(
                    "{ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, c.WHITE
                )

                elapsed_rect = elapsed_time_display.get_rect()
                elapsed_rect.top = 0
                elapsed_rect.right = settings['WIDTH']
                screen.blit(elapsed_time_display, elapsed_rect)

    def draw_cursor(self, screen):
        """
        Draw a cursor to the screen

        :param screen: the screen to draw to
        """
        cursor = h.load('cursor.png')
        cursor_rect = cursor.get_rect()
        cursor_rect.center = pygame.mouse.get_pos()
        screen.blit(cursor, cursor_rect)

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
        self.draw_cursor(screen)

        if settings['SHOW_NODES']:
            node_sprite = h.load('bullet.png')
            node_pos = node_sprite.get_rect()

            for node in self.world.nodes.nodes:
                node_pos.center = node
                screen.blit(node_sprite, node_pos)

    def update(self):
        """
        Recalculate the positions of everything in the world.

        Additionally, check the Hero's health
        """
        self.hero.update()
        self.world.update(self.hero)

        if self.hero.hp <= 0:
            self.logger.info('Hero Died')
            self.logger.debug('go to DeathScreen')
            self.die()

        if not self.hero.run_timer:
            self.logger.info('Hero Won with time: {0}'.format(self.elapsed_time))
            self.logger.debug('go to WinScreen')
            self.win()

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
        self.tick_count += 1
        file_name = "{hero} - {seed}.txt".format(hero=self.hero.name, seed=self.seed)
        f = open(os.path.join("replays", file_name), 'a')
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings['LEFT']:
                    f.write('{tick} KeyDown Left\n'.format(tick=self.tick_count))

                    self.left_pressed = True
                    self.logger.info('pressed [LEFT]')

                    if self.hero.moving_right:
                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_right = False

                    self.world.changespeed(self.hero.actual_speed, 0)
                    self.hero.moving_left = True
                    self.hero.last_motion = 'left'

                elif event.key == settings['RIGHT']:
                    f.write('{tick} KeyDown Right\n'.format(tick=self.tick_count))

                    self.right_pressed = True
                    self.logger.info('pressed [RIGHT]')

                    if self.hero.moving_left:
                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_left = False

                    self.world.changespeed(-self.hero.actual_speed, 0)
                    self.hero.moving_right = True
                    self.hero.last_motion = 'right'

                elif event.key == settings['UP']:
                    f.write('{tick} KeyDown Up\n'.format(tick=self.tick_count))

                    self.logger.info('pressed [UP]')
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
                    f.write('{tick} KeyDown Bomb\n'.format(tick=self.tick_count))

                    self.logger.info('pressed [BOMB]')

                    if self.hero.bombs > 0:
                        bomb = self.hero.drop_bomb()
                        self.world.bomb_list.add(bomb)
                        self.world.all_sprites.add(bomb)

                elif event.key == settings['DOWN']:
                    f.write('{tick} KeyDown Down\n'.format(tick=self.tick_count))

                    self.logger.info('pressed [DOWN]')

                    for drop in self.world.drops_list:
                        if drop.is_weapon:
                            if hypot(drop.rect.centerx - self.hero.rect.centerx,
                                     drop.rect.centery - self.hero.rect.centery) <= self.hero.weapon_pickup_range:

                                if drop.drop.style == 0: # Melee
                                    if self.hero.melee_weapon is not None:
                                        self.logger.info('dropped old melee weapon ({0})'.format(self.hero.melee_weapon.name))
                                        self.world.all_sprites.add(self.hero.melee_weapon.sprite)
                                        self.world.drops_list.add(self.hero.melee_weapon.sprite)
                                    self.logger.info('picked up new melee weapon ({0})'.format(drop.drop.name))
                                    self.hero.melee_weapon = drop.drop

                                elif drop.drop.style == 1: # Ranged
                                    if self.hero.ranged_weapon is not None:
                                        self.logger.info('dropped old ranged weapon ({0})'.format(self.hero.ranged_weapon.name))
                                        self.world.all_sprites.add(self.hero.ranged_weapon.sprite)
                                        self.world.drops_sprites.add(self.hero.ranged_weapon.sprite)
                                    self.logger.info('picked up new ranged weapon ({0})'.format(drop.drop.name))
                                    self.hero.ranged_weapon = drop.drop
                                drop.kill()

                # Enter pause menu
                elif event.key == settings['PAUSE']:
                    self.logger.info('pressed [PAUSE]')

                    if settings['DEBUG'] and (pygame.key.get_mods() & pygame.KMOD_LSHIFT):
                        settings['GOD MODE'] = True
                        self.logger.info('God Mode Activated')
                    else:
                        self.logger.debug('Go to PauseScreen')
                        self.manager.go_to(PauseScreen(chosen_hero=type(self.hero), timer=self.timer, seed=self.seed))

            elif event.type == pygame.KEYUP:
                # Cancel the motion by adding the opposite of the keydown situation
                if event.key == settings['LEFT']:
                    f.write('{tick} KeyUp Left\n'.format(tick=self.tick_count))

                    self.left_pressed = False
                    self.logger.info('released [LEFT]')

                    if self.hero.moving_left:
                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_left = False

                    if self.right_pressed and not self.hero.moving_right:
                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_right = True
                        self.hero.last_motion = 'right'

                elif event.key == settings['RIGHT']:
                    f.write('{tick} KeyUp Right\n'.format(tick=self.tick_count))

                    self.right_pressed = False
                    self.logger.info('released [RIGHT]')

                    if self.hero.moving_right:
                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_right = False

                    if self.left_pressed and not self.hero.moving_left:
                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_left = True
                        self.hero.last_motion = 'left'

                elif event.key == settings['UP']:
                    f.write('{tick} KeyUp Up\n'.format(tick=self.tick_count))
                    self.logger.info('released [UP]')

                elif event.key == settings['DOWN']:
                    f.write('{tick} KeyUp Down\n'.format(tick=self.tick_count))
                    self.logger.info('released [DOWN]')

                elif event.key == settings['BOMB']:
                    f.write('{tick} KeyUp Bomb\n'.format(tick=self.tick_count))
                    self.logger.info('released [BOMB]')

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    self.logger.info('[Left Click] at {0}'.format(event.pos))

                    if self.hero.melee_weapon is not None:
                        for e in self.world.enemy_list:
                            dist = hypot(e.rect.centerx - self.hero.rect.centerx,
                                         e.rect.centery - self.hero.rect.centery)
                            if dist <= self.hero.melee_weapon.range:
                                e.damage(self.hero.melee_weapon.power * self.hero.actual_damage_multiplier)
                elif event.button == 3:  # Right Click
                    self.logger.info('[Right Click] at {0}'.format(event.pos))

            else:
                pass
        f.close()

    def die(self):
        self.manager.go_to(DeathScreen(self.timer, type(self.hero), self.seed))

    def win(self):
        self.manager.go_to(WinScreen(self.timer, type(self.hero), self.seed, self.elapsed_time))

    def create_world(self, n):
        """
        Generate the world and align the rooms.

        :param n: number of rooms to generate, passed to generate_world
        """

        self.logger.info('========Generating World With Seed {seed}========'.format(seed=self.seed))
        random.seed(self.seed)

        room_list = self.generate_world(n)
        aligned_rooms = self.align_doors(room_list)

        self.logger.info('==============Complete World Generated!==============')

        self.world = rooms.World(self.seed)
        self.world.room_array = aligned_rooms

        self.logger.info(' ')
        for row in aligned_rooms:
            self.logger.info(row.replace('&', ' '))

        self.logger.info(' ')
        self.logger.info('=====================================================')

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
                * If the same room is selected twice, generate a test value which must be greater than 5
        * Finally, add the ending room

        :param n: The Int number of rooms to randomly choose
        """

        room_list = []
        possible_rooms = [v for k, v in sorted(rooms.room_dict.items()) if k not in ["StartingRoom", "EndingRoom"]]

        room_list.append(rooms.room_dict["StartingRoom"])

        move_down_counter = 0
        move_left_counter = 0
        move_right_counter = 0

        self.logger.debug('Generating New World')

        for i in range(n):
            matched = False
            self.logger.debug('======finding room {i}======'.format(i=i))
            while not matched:
                possible_next_room = random.choice(possible_rooms)
                self.logger.debug('==new room==')
                for row in possible_next_room:
                    self.logger.debug(row)

                if possible_next_room[0] == rooms.MoveDown:
                    if move_down_counter <= 2:
                        if possible_next_room == room_list[-1]:
                            test = random.randint(0, 10)
                            self.logger.debug('Same room repeated. (move down) Test={0}'.format(test))
                            if test >= 5:
                                room_list.append(possible_next_room)

                                move_down_counter += 1
                                move_left_counter = 0
                                move_right_counter = 0

                                matched = True
                            else:
                                self.logger.debug('DQ: Test is not greater than threshold')
                        else:
                            room_list.append(possible_next_room)

                            move_down_counter += 1
                            move_left_counter = 0
                            move_right_counter = 0

                            matched = True
                    else:
                        self.logger.debug('DQ: too many down in a row')

                elif possible_next_room[0] == rooms.MoveLeft:
                    if move_left_counter <= 4:
                        if possible_next_room == room_list[-1]:
                            test = random.randint(0, 10)
                            self.logger.debug('Same room repeated. (move left) Test={0}'.format(test))
                            if test >= 5:
                                room_list.append(possible_next_room)

                                move_down_counter = 0
                                move_left_counter += 1
                                move_right_counter = 0

                                matched = True
                            else:
                                self.logger.debug('DQ: Test is not greater than threshold')
                        else:
                            room_list.append(possible_next_room)

                            move_down_counter = 0
                            move_left_counter += 1
                            move_right_counter = 0

                            matched = True
                    else:
                        self.logger.debug('DQ: too many left in a row')

                elif possible_next_room[0] == rooms.MoveRight:
                    if move_right_counter <= 4:
                        if possible_next_room == room_list[-1]:
                            test = random.randint(0, 10)
                            self.logger.debug('Same room repeated. (move right) Test={0}'.format(test))
                            if test >= 5:
                                room_list.append(possible_next_room)

                                move_down_counter = 0
                                move_left_counter = 0
                                move_right_counter += 1

                                matched = True
                            else:
                                self.logger.debug('DQ: Test is not greater than threshold')
                        else:
                            room_list.append(possible_next_room)

                            move_down_counter = 0
                            move_left_counter = 0
                            move_right_counter += 1

                            matched = True
                    else:
                        self.logger.debug('DQ: too many right in a row')

            self.logger.debug('move_down: {0}, move_left: {1}, move_right: {2}'.format(
                move_down_counter, move_left_counter, move_right_counter))

            self.logger.debug('=======found room {i}======'.format(i=i))

        room_list.append(rooms.room_dict["EndingRoom"])
        self.logger.debug('===============WorldGen Complete===============')

        return room_list

    def align_doors(self, room_list):
        """
        Align all the doors to create a world that is solvable

        * Cycle through the first door block at the bottom of the last room,
        * Then find the first door block at the top of the new room,
        * Finally add a bunch of blank characters (spaces) to offset the new room until
            the doors line up
        """
        self.logger.debug('===Begin modifying rooms to align doors===')
        room_array = []
        for index, room in enumerate(room_list):
            self.logger.debug(' ')
            self.logger.debug('next room: {0}'.format(index))

            room = room[1:]  # get rid of the leading "move right" identifier

            for row in room:
                self.logger.debug(row)

            if len(room_array) == 0:
                room_array += room

            else:
                #Find the position of the previous room's exit door
                self.logger.debug(' ')
                self.logger.debug('Previous room exit')
                self.logger.debug(room_array[-1])

                previous_door_location = room_array[-1].find('DD')
                self.logger.debug("previous door location: {0}".format(previous_door_location))

                #Find the position of the new room's entrance door
                self.logger.debug(' ')
                self.logger.debug('Current room entrance')
                self.logger.debug(room[0])

                new_door_location = room[0].find('DD')
                self.logger.debug("new door location: {0}".format(new_door_location))


                #Get the distance between the two doors
                door_location = previous_door_location - new_door_location
                self.logger.debug('net door location (prev - new): {0}'.format(door_location))

                aligned_room = []
                if door_location >= 0:
                    self.logger.debug('---Adding spaces to the room to push it right---')
                    self.logger.debug(room_array[-1])
                    for row in room:
                        # Add & (blank tile) to each row to line up its door with the previous room
                        aligned_row = "&"*abs(door_location) + row
                        aligned_room.append(aligned_row)

                else:
                    self.logger.debug('--Adding spaces to the rest of the world to relatively push the new one left---')
                    for index2, row in enumerate(room_array):
                        aligned_row = "&"*abs(door_location) + row
                        room_array[index2] = aligned_row

                    for row in room:
                        aligned_room.append(row)

                room_array += aligned_room

        self.logger.debug('----====Finished World====----')

        return room_array


class DeathScreen(Menu):
    """
    A game state for showing the hero's death.

    Returns to title screen when any button is pressed,
    Show "you lose" text alongside the seed of the world
    that was played.
    """

    musicfile = 'Raven.mp3'

    title = "You Died!"
    options = ["Retry", "Save Seed[WIP]", "Generate New World", "Quit"]

    show_back_button = False

    def __init__(self, timer, chosen_hero, seed):
        super().__init__()
        self.manager = None
        self.seed = seed
        self.timer = timer
        self.chosen_hero = chosen_hero

        self.selections = [InGame(timer=self.timer, chosen_hero=self.chosen_hero, seed=self.seed),
                           "seed: {0}".format(self.seed),
                           ChooseHero(),
                           TitleScreen()
        ]


    def extra_draw(self, screen):
        seed_text = h.load_font("luximb.ttf", 16).render(
            "SEED: {0}".format(self.seed), 1, c.BLUE
        )
        seed_rect = seed_text.get_rect()
        seed_rect.right = settings['WIDTH']
        seed_rect.bottom = settings['HEIGHT']
        screen.blit(seed_text, seed_rect)


class WinScreen(Menu):
    """
    A gamestate for showing a victory.

    Returns to title screen when any button is pressed,
    Show "you win" text alongside the seed of the world
    that was played.
    """

    title = "You Win!"
    options = ["Retry", "Save Seed[WIP]", "Generate New World", "Quit"]
    show_back_button = False

    def __init__(self, timer, chosen_hero, seed, elapsed_time):
        super().__init__()
        self.manager = None
        self.seed = seed
        self.elapsed_time = elapsed_time
        self.timer = timer
        self.chosen_hero = chosen_hero

        self.selections = [InGame(timer=self.timer, chosen_hero=self.chosen_hero, seed=self.seed),
                           "seed: {0}".format(self.seed),
                           ChooseHero(),
                           TitleScreen()
        ]

    def extra_draw(self, screen):
        # Print the final time
        partials = self.elapsed_time % 60
        seconds = ((self.elapsed_time - partials) // 60) % 60
        minutes = (((self.elapsed_time - partials) // 60) - seconds) // 60
        if len(str(partials)) != 2:
            partials = "0" + str(partials)
        if len(str(seconds)) != 2:
            seconds = "0" + str(seconds)
        if len(str(minutes)) != 2:
            minutes = "0" + str(minutes)
        formatted_elapsed_time = "{minutes}:{seconds}:{partials}".format(minutes=minutes, seconds=seconds, partials=partials)
        elapsed_time_display = h.load_font('luximb.ttf', 48).render(
            "Final Time: {ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, c.GREEN
        )
        elapsed_time_display_rect = elapsed_time_display.get_rect()
        elapsed_time_display_rect.center = (settings['WIDTH']/2, settings['HEIGHT']/2)
        elapsed_time_display_rect.y += .15*settings['HEIGHT']
        screen.blit(elapsed_time_display, elapsed_time_display_rect)

        # Print the seed
        seed_text = h.load_font("luximb.ttf", 16).render(
            "SEED: {0}".format(self.seed), 1, c.BLUE
        )
        seed_rect = seed_text.get_rect()
        seed_rect.right = settings['WIDTH']
        seed_rect.bottom = settings['HEIGHT']
        screen.blit(seed_text, seed_rect)

    def update(self):
        pass


class PauseScreen(Menu):
    title = "Pause"
    options = ["Resume", "Restart", "Quit"]

    show_back_button = False

    def __init__(self, timer, chosen_hero, seed):
        super().__init__()
        self.timer = timer
        self.chosen_hero = chosen_hero
        self.seed = seed
        self.selections = ['go back', InGame(timer=self.timer, chosen_hero=self.chosen_hero, seed=self.seed), TitleScreen()]

    def extra_draw(self, screen):
        """
        Print the seed
        """
        seed_text = h.load_font("luximb.ttf", 16).render(
            "SEED: {0}".format(self.seed), 1, c.BLUE
        )
        seed_rect = seed_text.get_rect()
        seed_rect.right = settings['WIDTH']
        seed_rect.bottom = settings['HEIGHT']
        screen.blit(seed_text, seed_rect)


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
