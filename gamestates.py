"""
Store all the game states as classes that are instantiated.
"""
import datetime
import pickle
import random
import pygame
from config import settings
import constants
import helpers as h
import rooms
import hero


class GameState(object):
    """
    A superclass for all the states the game can be in.

    musicfile is a string representing the name of background music to be played.
    """

    musicfile = None

    def __init__(self):
        pass

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


class TitleScreen(GameState):
    """
    The title screen game state.
    """

    musicfile = 'O_Fortuna.mp3'

    def __init__(self):
        super().__init__()
        self.manager = None

        self.selected = 0

    def draw(self, screen):
        """
        Draw a TitleScreen with text telling the user to press SPACE to begin
        :param screen: The pygame screen on which to draw
        """
        background = h.create_background(h.load('sand.jpg'))
        screen.blit(background, (0, 0))

        font = h.load_font('BLKCHCRY.TTF', 32)

        welcome_text = h.load_font('BLKCHCRY.TTF', 48).render(
            "Welcome to mineEye!", 1, constants.BLACK
        )
        h.blit_text(welcome_text, screen, 1)

        begin_text = font.render(
            "Start!", 1, constants.BLACK
        )
        begin_rect = h.blit_text(begin_text, screen, 2)

        begin_timer_text = font.render(
            "Time Trial!", 1, constants.BLACK
        )
        timer_rect = h.blit_text(begin_timer_text, screen, 3)

        options_text = font.render(
            "Settings!", 1, constants.BLACK
        )
        options_rect = h.blit_text(options_text, screen, 4)

        quit_text = font.render(
            "Quit", 1, constants.BLACK
        )
        quit_rect = h.blit_text(quit_text, screen, 5)

        selected_indicator = h.load('pickaxe.png')
        selected_rect = selected_indicator.get_rect()

        if self.selected == 0:
            selected_rect.left = begin_rect.right
            selected_rect.centery = begin_rect.centery
        elif self.selected == 1:
            selected_rect.left = timer_rect.right
            selected_rect.centery = timer_rect.centery
        elif self.selected == 2:
            selected_rect.left = options_rect.right
            selected_rect.centery = options_rect.centery
        elif self.selected == 3:
            selected_rect.left = quit_rect.right
            selected_rect.centery = quit_rect.centery

        screen.blit(selected_indicator, selected_rect)

    def update(self):
        pass

    def handle_events(self, events):
        """
        Wait for a keystroke to move forward with the game.
        UP and DOWN will move through options
        SPACE or RIGHT will execute the currently selected option

        Overwrites the default handle_events from the parent GameState class.
        """
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == settings['DOWN']:
                    if self.selected < 3:
                        self.selected += 1
                elif e.key == settings['UP']:
                    if self.selected > 0:
                        self.selected -= 1
                elif e.key == pygame.K_SPACE or e.key == settings['RIGHT']:
                    if self.selected == 0:
                        self.manager.go_to(ChooseHero())
                    elif self.selected == 1:
                        self.manager.go_to(ChooseHero(timer=True))
                    elif self.selected == 2:
                        self.manager.go_to(ChangeSettings())
                    elif self.selected == 3:
                        self.manager.done = True


class ChooseHero(GameState):
    """
    A game state for choosing a hero to play as.
    """

    def __init__(self, timer=False):
        super().__init__()
        self.manager = None

        self.selected = 0

        self.timer = timer

    def draw(self, screen):
        """
        Draw a selection menu with a picture of the heros.
        """
        background = h.create_background(h.load('sand.jpg'))
        screen.blit(background, (0, 0))

        font = h.load_font('MelmaCracked.ttf', 32)
        desc_font = h.load_font('MelmaCracked.ttf', 24)

        title_text = h.load_font('MelmaCracked.ttf', 48).render(
            "Choose a Hero!", 1, constants.BLACK
        )
        h.blit_text(title_text, screen, 1)

        i = 2
        rect_list = []
        for possible_hero in hero.hero_list:
            name_text = font.render(
                possible_hero.name, 1, constants.BLACK
            )
            name_rect = h.blit_text(name_text, screen, i)

            desc_text = desc_font.render(
                possible_hero.description, 1, constants.BLACK
            )
            desc_rect = desc_text.get_rect()
            desc_rect.top = name_rect.bottom
            desc_rect.centerx = name_rect.centerx
            screen.blit(desc_text, desc_rect)

            rect_list.append(desc_rect)

            i += 1

        selected_indicator = h.load('pickaxe.png')
        selected_rect = selected_indicator.get_rect()

        if self.selected == 0:
            selected_rect.left = rect_list[0].right
            selected_rect.bottom = rect_list[0].bottom
        elif self.selected == 1:
            selected_rect.left = rect_list[1].right
            selected_rect.bottom = rect_list[1].bottom
        elif self.selected == 2:
            selected_rect.left = rect_list[2].right
            selected_rect.bottom = rect_list[2].bottom

        screen.blit(selected_indicator, selected_rect)

    def update(self):
        pass

    def handle_events(self, events):
        """
        Wait for a keystroke to move forward with the game.
        UP and DOWN will move through options
        SPACE or RIGHT will execute the currently selected option

        Overwrites the default handle_events from the parent GameState class.
        """
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == settings['DOWN']:
                    if self.selected <= 2:
                        self.selected += 1
                elif e.key == settings['UP']:
                    if self.selected >= 1:
                        self.selected -= 1
                elif e.key == settings['LEFT']:
                    self.manager.go_to(TitleScreen())
                elif e.key == pygame.K_SPACE or e.key == settings['RIGHT']:
                    if self.selected == 0:
                        self.manager.go_to(InGame(timer=self.timer, chosen_hero=hero.hero_list[0]))
                    elif self.selected == 1:
                        self.manager.go_to(InGame(timer=self.timer, chosen_hero=hero.hero_list[1]))
                    elif self.selected == 2:
                        self.manager.go_to(InGame(timer=self.timer, chosen_hero=hero.hero_list[2]))


class ChangeSettings(GameState):
    """
    A game state for changing local variables like PLAY_MUSIC.
    """

    def __init__(self):

        super().__init__()
        self.manager = None

        self.selected = 0

    def draw(self, screen):
        """
        Draw a menu with configuration options.
        :param screen: The pygame screen on which to draw.
        """
        background = h.create_background(h.load('sand.jpg'))
        screen.blit(background, (0, 0))

        font = h.load_font('MelmaCracked.ttf', 32)

        on = h.load_font('MelmaCracked.ttf', 16).render(
            'On', 1, constants.BLACK
        )

        off = h.load_font('MelmaCracked.ttf', 16).render(
            'Off', 1, constants.BLACK
        )

        option_text = h.load_font('MelmaCracked.ttf', 48).render(
            "Options", 1, constants.BLACK
        )
        h.blit_text(option_text, screen, 1)

        music_text = font.render(
            'Play Music', 1, constants.BLACK
        )
        music_rect = h.blit_text(music_text, screen, 2)

        if settings['PLAY_MUSIC']:
            on_rect = on.get_rect()
            on_rect.left = music_rect.right
            on_rect.centery = music_rect.centery
            screen.blit(on, on_rect)
        else:
            off_rect = off.get_rect()
            off_rect.left = music_rect.right
            off_rect.centery = music_rect.centery
            screen.blit(off, off_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == settings['DOWN']:
                    pass
                elif e.key == settings['UP']:
                    pass
                elif e.key == settings['LEFT']:
                    self.manager.go_to(TitleScreen())
                elif e.key == pygame.K_SPACE or e.key == settings['RIGHT']:
                    if self.selected == 0:
                        if settings['PLAY_MUSIC']:
                            settings['PLAY_MUSIC'] = False

                        else:
                            settings['PLAY_MUSIC'] = True

                        f = open('settings', 'wb')
                        f.write(pickle.dumps(settings))
                        f.close()


class InGame(GameState):
    """
    A game state for moving and falling through the mine
    """

    musicfile = 'Pathetique.mp3'

    def __init__(self, timer=False, chosen_hero=hero.Normal):
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
        self.generate_world(25)
        self.hero.world = self.world

        self.timer = timer
        self.elapsed_time = 0

        self.left_pressed = False
        self.right_pressed = False

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

        hero_hp = h.load_font('BLKCHCRY.TTF', 32).render(
            "HP: {0}".format(self.hero.hp), 1, constants.WHITE
        )
        screen.blit(hero_hp, (0, 0))

        if self.timer:
            if self.hero.run_timer:
                self.elapsed_time = datetime.datetime.now() - self.start_time
                formatted_elapsed_time = self.elapsed_time.total_seconds()

                elapsed_time_display = h.load_font('BLKCHCRY.TTF', 20).render(
                    "{ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, constants.WHITE
                )

                time_pos = (constants.TOP_RIGHT[0] - elapsed_time_display.get_rect().width - 16, 0)
                screen.blit(elapsed_time_display, time_pos)
            else:
                formatted_elapsed_time = self.elapsed_time.total_seconds()
                elapsed_time_display = h.load_font('BLKCHCRY.TTF', 48).render(
                    "Final Time: {ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, constants.GREEN
                )
                elapsed_time_display_rect = elapsed_time_display.get_rect()
                elapsed_time_display_rect.center = constants.CENTER
                screen.blit(elapsed_time_display, elapsed_time_display_rect)

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
        These events include:
            key presses
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

                elif event.key == settings['DOWN']:
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
        screen.fill(constants.BLACK)
        death_text = h.load_font("Melma.ttf", 32).render(
            "You Died! \n Press any key to try again.", 1, constants.RED
        )
        death_text_x = death_text.get_rect().width / 2
        death_text_y = death_text.get_rect().height / 2
        centered_pos = (constants.CENTER[0] - death_text_x, constants.CENTER[1] - death_text_y)

        screen.blit(death_text, centered_pos)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.manager.go_to(TitleScreen())