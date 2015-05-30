"""
Store all the game states as classes that are instantiated.
"""
import datetime
import random
import pygame
import config
import constants
import helpers as h
import rooms
from hero import Hero


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
        self.go_to(TitleScreen())

    def go_to(self, gamestate):
        """
        Change the game state to gamestate and add this class to the new gamestate's variables.

        If the new gamestate has a music file associated with it, play that music.
        """
        self.state = gamestate
        self.state.manager = self

        if gamestate.musicfile and config.PLAY_MUSIC:
            h.play_music(gamestate.musicfile)


class TitleScreen(GameState):
    """
    The title screen game state.
    """

    musicfile = 'O_Fortuna.mp3'

    def __init__(self):
        super().__init__()
        self.manager = None

    def draw(self, screen):
        """
        Draw a TitleScreen with text telling the user to press SPACE to begin
        :param screen: The pygame screen on which to draw
        """
        background = h.create_background(h.load('sand.jpg'))
        screen.blit(background, (0, 0))
        welcome_text = h.load_font('BLKCHCRY.TTF', 32).render(
            "Welcome to mineEye! Press SPACE or T to begin!", 1, constants.BLACK
        )
        welcome_rect = welcome_text.get_rect()
        welcome_rect.centerx = screen.get_rect().centerx
        welcome_rect.centery = screen.get_rect().centery

        screen.blit(welcome_text, welcome_rect)

    def update(self):
        pass

    def handle_events(self, events):
        """
        Wait for a keystroke to move forward with the game. Space will go to a timerless game, whereas T will go to
        a timed game.

        Overwrites the default handle_events from the parent GameState class.
        """
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.manager.go_to(InGame())
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_t:
                self.manager.go_to(InGame(timer=True))


class InGame(GameState):
    """
    A game state for moving and falling through the mine
    """

    musicfile = 'Pathetique.mp3'

    def __init__(self, timer=False):
        """
        Instantiate the primary Game State.
        :param timer: A boolean. True if a timer is to be displayed in the top right, False if not.
        """
        super().__init__()
        self.manager = None

        self.all_sprites_list = pygame.sprite.Group()

        self.hero = Hero()
        self.all_sprites_list.add(self.hero)

        self.start_time = datetime.datetime.now()

        self.world = None
        self.generate_world(50)
        self.hero.world = self.world

        self.timer = timer

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
        self.all_sprites_list.draw(screen)

        hero_hp = h.load_font('BLKCHCRY.TTF', 32).render(
            "HP: {0}".format(self.hero.hp), 1, constants.WHITE
        )
        screen.blit(hero_hp, (0, 0))

        if self.timer:
            elapsed_time = datetime.datetime.now() - self.start_time
            formatted_elapsed_time = elapsed_time.total_seconds()
            elapsed_time_display = h.load_font('BLKCHCRY.TTF', 20).render(
                "{ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, constants.WHITE
            )
            screen.blit(elapsed_time_display, (950, 0))

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
            if config.KEY_CANCELING:

                if event.type == pygame.KEYDOWN:
                    if event.key == config.LEFT:
                        self.left_pressed = True

                        if self.hero.moving_right:
                            self.world.changespeed(self.hero.actual_speed, 0)
                            self.hero.moving_right = False

                        self.world.changespeed(self.hero.actual_speed, 0)
                        self.hero.moving_left = True

                    elif event.key == config.RIGHT:
                        self.right_pressed = True

                        if self.hero.moving_left:
                            self.world.changespeed(-self.hero.actual_speed, 0)
                            self.hero.moving_left = False

                        self.world.changespeed(-self.hero.actual_speed, 0)
                        self.hero.moving_right = True

                    elif event.key == config.UP:
                        if not self.hero.jumping:
                            self.world.changespeed(0, 12)
                            self.hero.jumping = True

                    elif event.key == config.DOWN:
                        pass
                    # Quit to TitleScreen (eventually pause menu) if the user presses escape
                    elif event.key == config.PAUSE:
                        self.manager.go_to(TitleScreen())

                elif event.type == pygame.KEYUP:
                    # Cancel the motion by adding the opposite of the keydown situation
                    if event.key == config.LEFT:
                        self.left_pressed = False

                        if self.hero.moving_left:
                            self.world.changespeed(-self.hero.actual_speed, 0)
                            self.hero.moving_left = False

                        if self.right_pressed and not self.hero.moving_right:
                            self.world.changespeed(-self.hero.actual_speed, 0)
                            self.hero.moving_right = True

                    elif event.key == config.RIGHT:
                        self.right_pressed = False

                        if self.hero.moving_right:
                            self.world.changespeed(self.hero.actual_speed, 0)
                            self.hero.moving_right = False

                        if self.left_pressed and not self.hero.moving_left:
                            self.world.changespeed(self.hero.actual_speed, 0)
                            self.hero.moving_left = True

                    elif event.key == config.UP:
                        pass

                    elif event.key == config.DOWN:
                        pass


            else:  # Key Canceling is False
                if event.type == pygame.KEYDOWN:
                    if event.key == config.LEFT:
                        self.world.changespeed(self.hero.actual_speed, 0)

                    elif event.key == config.RIGHT:
                        self.world.changespeed(-self.hero.actual_speed, 0)

                    elif event.key == config.UP:
                        if not self.hero.jumping:
                            self.world.changespeed(0, 12)
                            self.hero.jumping = True

                    elif event.key == config.DOWN:
                        pass
                    # Quit to TitleScreen (eventually pause menu) if the user presses escape
                    elif event.key == config.PAUSE:
                        self.manager.go_to(TitleScreen())

                elif event.type == pygame.KEYUP:
                    # Cancel the motion by adding the opposite of the keydown situation
                    if event.key == config.LEFT:
                        self.world.changespeed(-self.hero.actual_speed, 0)

                    elif event.key == config.RIGHT:
                        self.world.changespeed(self.hero.actual_speed, 0)

                    elif event.key == config.UP:
                        pass

                    elif event.key == config.DOWN:
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
                    if move_left_counter <= 1:  # Gets around small bug with moving left too many times
                        room_list.append(possible_next_room)

                        move_down_counter = 0
                        move_left_counter += 1
                        move_right_counter = 0
                        matched = True

                elif possible_next_room[0] == rooms.MoveRight:
                    if move_right_counter <= 3:
                        room_list.append(possible_next_room)

                        move_down_counter = 0
                        move_left_counter = 0
                        move_right_counter += 1
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