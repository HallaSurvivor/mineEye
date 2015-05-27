"""
Store all the game states as classes that are instantiated.
"""
import datetime
import pygame
import config
import constants
import spritenames as sn
import rooms

class GameState(object):
    """
    A superclass for all the states the game can be in.
    """
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
        change the game state to gamestate and add this class to the new gamestate's variables.
        """
        self.state = gamestate
        self.state.manager = self


class TitleScreen(GameState):
    """
    The title screen game state.
    """

    def __init__(self):
        super().__init__()
        self.manager = None

    def draw(self, screen):
        """
        Draw a TitleScreen with text telling the user to press SPACE to begin
        :param screen: The pygame screen on which to draw
        """
        background = sn.create_background(sn.load('sand.jpg'))
        screen.blit(background, (0, 0))
        welcome_text = sn.load_font('BLKCHCRY.TTF', 32).render(
            "Welcome to mineEye! Press SPACE to begin!", 1, constants.BLACK
        )
        welcome_text_x = welcome_text.get_rect().width / 2
        welcome_text_y = welcome_text.get_rect().height / 2
        centered_pos = (constants.CENTER[0] - welcome_text_x, constants.CENTER[1] - welcome_text_y)

        screen.blit(welcome_text, centered_pos)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.manager.go_to(InGame())


class InGame(GameState):
    """
    A game state for moving and falling through the mine
    """

    def __init__(self):
        super().__init__()
        self.manager = None

        self.all_sprites_list = pygame.sprite.Group()

        self.hero = sn.Hero()
        self.all_sprites_list.add(self.hero)
        self.start_time = datetime.datetime.now()
        self.world = None
        self.generate_world()

        self.world.world_shift_x = 0
        self.world.world_shift_y = 0

    def draw(self, screen):
        self.world.draw(screen)
        self.all_sprites_list.draw(screen)

        hero_hp = sn.load_font('BLKCHCRY.TTF', 32).render(
            "HP: {0}".format(self.hero.hp), 1, constants.WHITE
        )
        screen.blit(hero_hp, (0, 0))

        elapsed_time = datetime.datetime.now() - self.start_time
        formatted_elapsed_time = elapsed_time.total_seconds()
        elapsed_time_display = sn.load_font('BLKCHCRY.TTF', 20).render(
            "{ElapsedTime}".format(ElapsedTime=formatted_elapsed_time), 1, constants.WHITE
        )
        screen.blit(elapsed_time_display, (950, 0))


    def update(self):
        self.hero.move(self.world.block_list, self.world)

        if self.hero.hp <= 0:
            self.manager.go_to(DeathScreen())

    def handle_events(self, events):

        for event in events:
            if event.type == pygame.KEYDOWN:
                # Create the motion by changing the Hero's speed vector
                if event.key == config.LEFT:
                    self.hero.changespeed(3, 0)
                elif event.key == config.RIGHT:
                    self.hero.changespeed(-3, 0)
                elif event.key == config.UP:
                    self.hero.changespeed(0, 3)
                elif event.key == config.DOWN:
                    self.hero.changespeed(0, -3)

            elif event.type == pygame.KEYUP:
                # Cancel the motion by adding the opposite of the keydown situation
                if event.key == config.LEFT:
                    self.hero.changespeed(-3, 0)
                elif event.key == config.RIGHT:
                    self.hero.changespeed(3, 0)
                elif event.key == config.UP:
                    self.hero.changespeed(0, -3)
                elif event.key == config.DOWN:
                    self.hero.changespeed(0, 3)



    def die(self):
        self.manager.go_to(DeathScreen())

    def generate_world(self):
        """
        TODO - make this generate a series of 50 rooms stacked together
            take things into consideration such as:

            not having a bunch of rooms going to the right in a row
            size of door (1 tile vs 2 tiles)

        """
        self.world = rooms.Room_01()

class DeathScreen(GameState):
    """
    A game state for showing the hero's death.
    """

    def __init__(self):
        super().__init__()
        self.manager = None

    def draw(self, screen):
        screen.fill(constants.BLACK)
        death_text = sn.load_font("Melma.ttf", 32).render(
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