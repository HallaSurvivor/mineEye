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
import time
import logging
import json
import random
import pygame
from dependencies.PathGetter import PathGetter
from config import settings
import constants as c
import rooms as r
import helpers as h
import world
import hero
import upgrades

module_logger = logging.getLogger('mineEye.gamestates')
seeds = h.load_seed_file()


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

    def draw_cursor(self, screen):
        """
        Draw a cursor to the screen

        :param screen: the screen to draw to
        """
        cursor = h.load('cursor.png')
        cursor_rect = cursor.get_rect()
        cursor_rect.center = pygame.mouse.get_pos()
        screen.blit(cursor, cursor_rect)

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
        self.logger = logging.getLogger('mineEye.gamestates.GameStateManager')

        self.done = False
        self.replay = False

        self.state = None
        self.go_to(TitleScreen())
        self.previous_state = None

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
    show_on_off = False

    def __init__(self):
        super().__init__()
        self.manager = None

        self.logger = logging.getLogger('mineEye.gamestates.Menu')

        self.beep = h.load_sound('select.wav')

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

        self.draw_background(screen)

        if not self.rect_list:
            self.rect_list = h.create_menu(screen, self.title, self.options, self.descriptions)
        else:
            h.create_menu(screen, self.title, self.options, self.descriptions)

        if self.show_on_off:
            self.draw_on_off(screen)

        if self.show_back_button:
            self.draw_back_button(screen)

        self.draw_selection_indicator(screen)
        self.extra_draw(screen)
        self.draw_cursor(screen)  # inherited from GameState

    def draw_background(self, screen):
        """
        draw the background
        """
        if self.default_background.get_size() != screen.get_size():
            self.default_background = h.create_background(h.load(self.background_tile))
        screen.blit(self.default_background, (0, 0))

    def draw_on_off(self, screen):
        """
        Draw the on/off labels beside settings
        """
        on = h.load_font('melma.ttf', 16).render(
            'On', 1, c.BLACK
        )

        off = h.load_font('melma.ttf', 16).render(
            'Off', 1, c.BLACK
        )
        try:
            for index, option in enumerate(self.selections):
                try:
                    if settings[option]:
                        on_rect = on.get_rect()
                        on_rect.bottomright = self.rect_list[index].bottomleft
                        screen.blit(on, on_rect)
                    else:
                        off_rect = off.get_rect()
                        off_rect.bottomright = self.rect_list[index].bottomleft
                        screen.blit(off, off_rect)
                except KeyError:  # GameState classes and other navigation options
                    pass

        except AttributeError:
            self.logger.error('Tried to draw on/off in menu without self.selections: {0}'.format(type(self)))

    def draw_selection_indicator(self, screen):
        """
        draw the image showing which option is selected to the screen
        """
        selected_indicator = h.load('pickaxe.png')
        selected_rect = selected_indicator.get_rect()
        selected_rect.bottomleft = self.rect_list[self.selected].bottomright
        screen.blit(selected_indicator, selected_rect)

    def draw_back_button(self, screen):
        """
        draw a back button and append 'go back' to the list of options
        """
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
        try:
            selected_option = self.selections[self.selected]
            if settings['PLAY_SFX']:
                self.beep.play()

            if selected_option == 'go back':
                self.manager.go_back()

            else:
                try:
                    new_seed = selected_option[5:]
                    int(new_seed)  # Purely to prove that we ARE dealing with a seed and move out of the "try:" if not
                    found = False
                    for index, current_seed in enumerate(seeds):
                        if current_seed == '' and not found:
                            self.add_seed(index, new_seed)
                            found = True
                    else:
                        if found:
                            self.manager.go_to(TitleScreen())
                        else:
                            self.logger.INFO('Tried to add seed {0}, but there were no available slots'.format(new_seed))
                            self.manager.go_to(TitleScreen(
                                error='Tried to add seed {0}, but there were no available slots'.format(new_seed))
                            )

                except ValueError:
                    self.toggle_setting(selected_option)

                except TypeError:
                    self.manager.go_to(selected_option)

        except AttributeError:  # Selected option is None
            pass

    def add_seed(self, index, seed):
        """
        Add a seed to the seeds list at a given index and store it
        """
        global seeds

        seeds[index] = seed
        with open('seeds.txt', 'w') as f:
            json.dump(seeds, f)

    def toggle_setting(self, setting):
        """
        Toggle a given setting between True and False, then save the dictionary
        """
        if settings[setting]:
            settings[setting] = False

        else:
            settings[setting] = True

        with open('settings.txt', 'w') as f:
            json.dump(settings, f)

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
            elif event.key == settings['LEFT'] or event.key == pygame.K_LEFT or event.key == pygame.K_ESCAPE:
                if self.show_back_button:
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

    title = 'Press Space to begin!'
    options = ['Start!', 'My Maps', 'Replays', 'Settings!', 'Quit!']

    musicfile = 'Pathetique.mp3'

    show_back_button = False

    def __init__(self, error=None):
        super().__init__()
        self.error = error
        self.selections = [InGame(seed=h.generate_seed()), PlayerMaps(), ChooseReplay(), ChangeSettings(), Quit()]

    def extra_draw(self, screen):
        """
        Draw errors to the screen
        """
        if self.error is not None:
            errmsg = h.load_font('melma.ttf', 16).render(self.error, 1, c.BLACK)
            screen.blit(errmsg, (5, 5))


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
                self.selections.append(InGame(seed=int(option)))


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
                self.selections.append(InGame(seed=int(option)))


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
            with open('seeds.txt', 'w') as f:
                json.dump(seeds, f)
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


class ChooseReplay(Menu):
    title = 'Choose Replay'
    options = ['Enter']

    def __init__(self):
        super().__init__()
        self.replay_location = ""
        self.selections = [None]

    def select_option(self):
        try:
            p = PathGetter.get()
            seed = str(p)[str(p).find('seed ') + 5:-5]  # 5 ahead of 'seed ' to compensate for letters,
                                                        # -5 to compensate for .txt
            if p:
                self.manager.go_to(InGame(seed=int(seed), replay_location=p))

        except FileNotFoundError:
            self.manager.go_to(TitleScreen('Sorry, Replays seem to be broken on your system. I\'m working on it!'))


class ChangeSettings(Menu):
    """
    A game state for changing local variables like PLAY_MUSIC.
    """
    title = "Settings"
    options = ["Play Music", "Play Sound Effects", "Change Keybinds"]

    show_on_off = True

    def __init__(self):
        super().__init__()
        self.selections = ['PLAY_MUSIC', 'PLAY_SFX', ChangeBinds()]


class ChangeBinds(Menu):
    """
    A place to change keybinds.
    """
    title = "KeyBinds"
    options = ["Up", "Left", "Right", "Down", "Bomb", "Pause"]
    selections = [string.upper() for string in options]

    allow_on_off = False

    def __init__(self):

        super().__init__()

        self.modifying = False
        try:
            self.descriptions = [pygame.key.name(settings[option]) for option in self.selections]
        except KeyError: # go back
            pass

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
            pygame.K_BACKSLASH, pygame.K_QUOTE, pygame.K_TAB,
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
                    elif e.key == settings['LEFT'] or e.key == pygame.K_LEFT or e.key == pygame.K_ESCAPE:
                        self.manager.go_back()
                    elif e.key == pygame.K_SPACE or e.key == settings['RIGHT'] or \
                            e.key == pygame.K_RIGHT or e.key == pygame.K_RETURN:
                        try:
                            self.options[self.selected] = ">" + self.options[self.selected] + "<"
                            self.modifying = True
                        except IndexError:  # 'go back' is not listed, and will throw an IndexError
                            self.manager.go_back()

                else:  # If we are modifying a bind
                    if e.key == pygame.K_ESCAPE or e.key == pygame.K_RETURN or e.key == pygame.K_LEFT:
                        self.options[self.selected] = self.options[self.selected][1:-1]  # cut the > and <
                        self.modifying = False

                    else:
                        if e.key in valid_options:
                            # If the key is not already bound
                            if e.key not in [settings[selection] for selection in self.selections
                                             if selection != 'go back']:
                                settings[self.selections[self.selected]] = e.key

                            else:  # If the key is already bound, pick a random key and bind it to the old option
                                for selection in self.selections:
                                    try:
                                        if settings[selection] == e.key:
                                            # Get a list of all the unbound, legal, keys
                                            unbound = [key for key in valid_options if key not in
                                                       [settings[selection] for selection in self.selections
                                                        if selection != 'go back']]

                                            new_key = random.choice(unbound)
                                            settings[selection] = new_key
                                    except KeyError:  # 'go back'
                                        pass

                                settings[self.selections[self.selected]] = e.key

                            self.options[self.selected] = self.options[self.selected][1:-1]
                            self.modifying = False

                            with open('settings.txt', 'w') as f:
                                json.dump(settings, f)

            if not self.modifying:
                if e.type == pygame.MOUSEMOTION:
                    pos = e.pos
                    for index, rect in enumerate(self.rect_list):
                        if rect.collidepoint(pos):
                            self.selected = index

                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    pos = e.pos
                    for index, rect in enumerate(self.rect_list):
                        if rect.collidepoint(pos):
                            try:
                                self.options[self.selected] = ">" + self.options[self.selected] + "<"
                                self.modifying = True
                            except IndexError:
                                self.manager.go_back()


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

    def __init__(self, seed, chosen_hero=None, replay_location=None, loop_count=0, tick=0):
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
        if chosen_hero:
            self.hero = chosen_hero
        else:
            self.hero = hero.Hero()

        self.room_number = 30  # number of rooms to generate
        self.loop_number = 5  # number of times you can loop

        self.loop_count = loop_count
        self.splits = []

        self.tick_count = tick
        self.start_time = time.strftime('%a %d %b %Y - %H %M %S')

        self.world = None

        self.left_pressed = False
        self.right_pressed = False

        self.show_circle = False

        if replay_location:
            self.replay = True
        else:
            self.replay = False

        if self.replay:
            with open(os.path.join(replay_location), 'r') as somefile:
                self.replay_list = [line for line in somefile]

        self.event_list = []

    def enter_world(self):
        """
        Create the world, and give the world to the Hero.

        Avoids generating the world multiple times due to
        multiple instances of GameState existing at once.
        """
        self.logger.info('--====NEW WORLD====--')
        self.create_world(self.room_number)
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
        if self.world.run_timer:
            partials = self.tick_count % 60
            seconds = ((self.tick_count - partials) // 60) % 60
            minutes = (((self.tick_count - partials) // 60) - seconds) // 60

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
        self.draw_cursor(screen)  # inherited from GameState

        if self.show_circle:
            try:
                pygame.draw.circle(screen, (0, 0, 0, 100), self.hero.rect.center,
                                   int(self.hero.melee_range_multiplier*self.hero.melee_weapon.range))
                self.show_circle = False
            except AttributeError:
                pass

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
        if self.manager.replay:
            for line in self.replay_list:
                if line.startswith(str(self.tick_count) + " "):
                    type_ = None
                    dict_ = {}
                    if 'KeyUp' in line:
                        type_ = pygame.KEYUP
                        dict_['key'] = settings[line.upper().replace("\n", "")[line.find('KeyUp') + 6:]]
                    elif 'KeyDown' in line:
                        type_ = pygame.KEYDOWN
                        dict_['key'] = settings[line.upper().replace("\n", "")[line.find('KeyDown') + 8:]]
                    elif 'Mouse1Down' in line:
                        type_ = pygame.MOUSEBUTTONDOWN
                        dict_['button'] = 1
                        dict_['pos'] = line[line.find('('):]
                    elif 'Mouse1Up' in line:
                        type_ = pygame.MOUSEBUTTONUP
                        dict_['button'] = 1
                        dict_['pos'] = line[line.find('('):]

                    self.event_list.append(pygame.event.Event(type_, dict_))

        else:
            self.manager.replay = self.replay

        self.hero.update()
        self.world.update(self.hero)

        if self.hero.hp <= 0:
            self.logger.info('Hero Died')
            self.logger.debug('go to DeathScreen')
            self.die()

        if not self.world.run_timer:
            self.logger.info('Hero Won with time: {0}'.format(self.tick_count))
            self.logger.debug('go to WinScreen')
            self.win()

    def handle_events(self, events):
        """
        Parse all of the events that pygame registers inside the class.

        All of the keys are defined inside of config.py, but can be
        overwritten by the user inside of the Change Keybinds menu
        defined above as ChangeBinds()

        The first bit of code is defining logging actions based on if
        the user is playing, or if it's a replay.

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
        if not self.replay:
            file_name = "{time} - seed {seed}.txt".format(time=self.start_time, seed=self.seed)
            f = open(os.path.join("replays", file_name), 'a')

            def log_down(key):
                self.logger.debug('pressed [{key}]'.format(key=key.upper()))
                f.write('{tick} KeyDown {key}\n'.format(tick=self.tick_count, key=key))

            def log_up(key):
                self.logger.debug('released [{key}]'.format(key=key.upper()))
                f.write('{tick} KeyUp {key}\n'.format(tick=self.tick_count, key=key))

            def log_m1down(pos):
                self.logger.debug('[Left Click Down] at {0}'.format(pos))
                f.write('{tick} Mouse1Down {pos}\n'.format(tick=self.tick_count, pos=pos))

            def log_m1up(pos):
                self.logger.debug('[Left Click Up] at {0}'.format(pos))
                f.write('{tick} Mouse1Up {pos}\n'.format(tick=self.tick_count, pos=pos))

            def log_m2down(pos):
                self.logger.debug('[Right Click Down] at {0}'.format(pos))
                f.write('{tick} Mouse2Down {pos}\n'.format(tick=self.tick_count, pos=pos))

            def log_m2up(pos):
                self.logger.debug('[Right Click Up] at {0}'.format(pos))
                f.write('{tick} Mouse2Up {pos}\n'.format(tick=self.tick_count, pos=pos))

        else:
            def log_down(key):
                self.logger.debug('replay pressed [{key}]'.format(key=key.upper()))

            def log_up(key):
                self.logger.debug('replay released [{key}]'.format(key=key.upper()))

            def log_m1down(pos):
                self.logger.debug('replay pressed Left Click at {0}'.format(pos))

            def log_m1up(pos):
                self.logger.debug('replay released Left Click at {0}'.format(pos))

            def log_m2down(pos):
                self.logger.debug('replay pressed Right Click at {0}'.format(pos))

            def log_m2up(pos):
                self.logger.debug('replay released Right Click at {0}'.format(pos))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == settings['LEFT']:
                    log_down('Left')
                    self.move_left()

                elif event.key == settings['RIGHT']:
                    log_down('Right')
                    self.move_right()

                elif event.key == settings['UP']:
                    log_down('Up')
                    self.jump()

                elif event.key == settings['BOMB']:
                    log_down('Bomb')
                    self.throw_bomb()

                elif event.key == settings['DOWN']:
                    log_down('Down')
                    self.pickup_weapon()

                # Enter pause menu
                elif event.key == settings['PAUSE'] or event.key == pygame.K_ESCAPE:
                    self.logger.debug('pressed [PAUSE]')
                    self.pause()  # Pause menu or GOD MODE

                elif event.key == pygame.K_j:
                    log_m1down(pygame.mouse.get_pos())
                    self.melee_attack()

            elif event.type == pygame.KEYUP:
                if event.key == settings['LEFT']:
                    log_up('Left')
                    self.stop_moving_left()

                elif event.key == settings['RIGHT']:
                    log_up('Right')
                    self.stop_moving_right()

                elif event.key == settings['UP']:
                    log_up('Up')

                elif event.key == settings['DOWN']:
                    log_up('Down')

                elif event.key == settings['BOMB']:
                    log_up('Bomb')

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    log_m1down(event.pos)
                    self.melee_attack()

                elif event.button == 3:  # Right Click
                    log_m2down(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    log_m1up(event.pos)

                elif event.button == 3:
                    log_m2up(event.pos)

            else:
                pass

        if self.manager.replay:
            self.event_list.clear()

        if not self.replay:
            f.close()

    def jump(self):
        """
        Called upon pressing the UP button

        * Move down and back to see if the Hero is on a platform
        * Jump
        * Double Jump if possible
        """

        if not self.hero.jumping:
            # Check if the hero is on a platform:
            self.hero.rect.y += 2
            hit_list = pygame.sprite.spritecollide(self.hero, self.world.block_list, False)
            self.hero.rect.y -= 2

            if len(hit_list) > 0:
                self.world.setspeed(None, self.hero.jump_height)
                self.hero.jumping = True
                self.hero.start_jump = True

        else:
            if self.hero.can_doublejump and not self.hero.double_jumping:
                self.world.setspeed(None, self.hero.double_jump_height)
                self.hero.double_jumping = True
                self.hero.start_double_jump = True

    def move_left(self):
        """
        Called upon pressing the LEFT button

        The works for non-canceled movement.
        i.e. pushing left while holding the right button,
        if you release left, you'll instantly move right.

        * Cancels motion right
        * Stores motion left
        * Causes motion left
        """
        self.left_pressed = True

        if self.hero.moving_right:
            self.world.setspeed(self.hero.actual_speed, None)
            self.hero.moving_right = False

        self.world.setspeed(self.hero.actual_speed, None)
        self.hero.moving_left = True
        self.hero.last_motion = 'left'

    def stop_moving_left(self):
        """
        Called upon releasing the LEFT button

        This is the brunt of the non-canceled
        movement logic.

        * Stop moving left
        * If RIGHT is pressed, start moving right
        """
        self.left_pressed = False

        if self.hero.moving_left:
            self.world.setspeed(0, None)
            self.hero.moving_left = False

        if self.right_pressed and not self.hero.moving_right:
            self.world.setspeed(-self.hero.actual_speed, None)
            self.hero.moving_right = True
            self.hero.last_motion = 'right'

    def move_right(self):
        """
        Called upon pressing the RIGHT button

        The works for non-canceled movement.
        i.e. pushing left while holding the right button,
        if you release left, you'll instantly move right.

        * Cancels motion left
        * Stores motion right
        * Causes motion right
        """

        self.right_pressed = True

        if self.hero.moving_left:
            self.world.setspeed(-self.hero.actual_speed, None)
            self.hero.moving_left = False

        self.world.setspeed(-self.hero.actual_speed, None)
        self.hero.moving_right = True
        self.hero.last_motion = 'right'

    def stop_moving_right(self):
        """
        Called upon releasing the RIGHT button

        This is the brunt of the non-canceled
        movement logic.

        * Stop moving right
        * If LEFT is pressed, start moving left
        """
        self.right_pressed = False

        if self.hero.moving_right:
            self.world.setspeed(0, None)
            self.hero.moving_right = False

        if self.left_pressed and not self.hero.moving_left:
            self.world.setspeed(self.hero.actual_speed, None)
            self.hero.moving_left = True
            self.hero.last_motion = 'left'

    def pickup_weapon(self):
        """
        Called upon pressing the DOWN button

        Pick up any weapon within the Hero's reach,
        and drop any currently held weapon

        """

        for weapon in self.world.drops_list:
            if weapon.is_weapon:
                if h.get_node_dist(weapon.rect, self.hero.rect) <= self.hero.weapon_pickup_range:

                    if weapon.drop.style == c.MELEE:
                        self.hero.pickup_melee_weapon(weapon)

                    elif weapon.drop.style == c.RANGED:
                        self.hero.pickup_ranged_weapon(weapon)

                    weapon.kill()

    def throw_bomb(self):
        """
        Called upon pressing the BOMB button

        spawn a bomb
        """

        if self.hero.bombs > 0:
            bomb = self.hero.drop_bomb()
            self.world.bomb_list.add(bomb)
            self.world.all_sprites.add(bomb)

    def pause(self):
        """
        Called upon pressing the PAUSE button

        Pauses the game, unless:
        * debug mode is on (config.py)
        * Left Shift is held

        In which case GOD MODE is activated.
            * Hero stops taking damage
            * Hero can jump super high

        This is for use in debugging things in game
        """
        if settings['DEBUG'] and (pygame.key.get_mods() & pygame.KMOD_LSHIFT):
            settings['GOD MODE'] = True
            self.logger.info('God Mode Activated')
        else:
            self.logger.debug('Go to PauseScreen')
            self.manager.go_to(PauseScreen(self.seed))

    def melee_attack(self):
        """
        Called when left clicking. Uses the Melee weapon
        """
        self.hero.melee_attack()
        self.show_circle = True

    def die(self):
        self.manager.replay = False
        self.manager.go_to(DeathScreen(self))

    def win(self):
        if self.loop_count < self.loop_number:
            self.loop_count += 1
            self.manager.go_to(UpgradeScreen(self))
        else:
            self.manager.replay = False
            self.manager.go_to(WinScreen(self))

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

        self.world = world.World(self.seed)
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
        possible_rooms = [v for k, v in sorted(r.room_dict.items())
                          if k not in ["StartingRoom", "EndingRoom", "TransitionRoom"]]

        room_list.append(r.room_dict["StartingRoom"])

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

                if possible_next_room[0] == c.MOVE_DOWN:
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

                elif possible_next_room[0] == c.MOVE_LEFT:
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

                elif possible_next_room[0] == c.MOVE_RIGHT:
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

        room_list.append(r.room_dict["EndingRoom"])
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

    title = "You Died!"
    options = ["Retry", "Save Seed", "Generate New World", "Quit"]

    show_back_button = False

    def __init__(self, game):
        super().__init__()
        self.manager = None
        self.seed = game.seed

        self.selections = [InGame(seed=self.seed),
                           "seed: {0}".format(self.seed),
                           InGame(seed=h.generate_seed()),
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


class UpgradeScreen(Menu):
    """
    A screen for displaying a random list of upgrades to the player between loops.
    """

    title = "Upgrade"
    show_back_button = False

    options = [' '] * 3

    def __init__(self, game):
        super().__init__()
        all_options = [k for k, v in sorted(upgrades.upgrades.items()) if k not in game.hero.upgrades]
        random.seed(game.seed + game.loop_count)
        self.options = random.sample(all_options, 3)
        self.values = [upgrades.upgrades[key] for key in self.options]
        self.game = game

    def select_option(self):
        self.values[self.selected](self.game.hero)
        self.manager.go_to(InGame(seed=self.game.seed, chosen_hero=self.game.hero,
                                  loop_count=self.game.loop_count, tick=self.game.tick_count))


class WinScreen(Menu):
    """
    A gamestate for showing a victory.

    Returns to title screen when any button is pressed,
    Show "you win" text alongside the seed of the world
    that was played.
    """

    title = "You Win!"
    options = ["Retry", "Save Seed", "Generate New World", "Quit"]
    show_back_button = False

    def __init__(self, game):
        super().__init__()
        self.manager = None
        self.seed = game.seed
        self.elapsed_time = game.tick_count

        self.selections = [InGame(seed=self.seed),
                           "seed: {0}".format(self.seed),
                           InGame(seed=h.generate_seed()),
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

    def __init__(self, seed):
        super().__init__()
        self.seed = seed
        self.selections = ['go back', InGame(self.seed), TitleScreen()]

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
