"""
Store all the game states as classes that are instantiated.
"""
import pygame
import config
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
            "Welcome to mineEye! Press SPACE to begin!", 1, config.BLACK
        )
        screen.blit(welcome_text, (200, 350))

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

        self.current_room = rooms.Room_01()

    def draw(self, screen):
        self.current_room.draw(screen)
        self.all_sprites_list.draw(screen)

        hero_hp = sn.load_font('BLKCHCRY.TTF', 32).render(
            "HP: {0}".format(self.hero.hp), 1, config.WHITE
        )
        screen.blit(hero_hp, (0, 0))

    def update(self):
        self.hero.move(self.current_room.block_list)

        if self.hero.hp <= 0:
            self.manager.go_to(DeathScreen())

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Create the motion by changing the Hero's speed vector
                if event.key == config.LEFT:
                    self.hero.changespeed(-3, 0)
                elif event.key == config.RIGHT:
                    self.hero.changespeed(3, 0)
                elif event.key == config.UP:
                    self.hero.changespeed(0, -3)  # Backwards because computer coords start in top left
                elif event.key == config.DOWN:
                    self.hero.changespeed(0, 3)  # Backwards because computer coords start in top left

            elif event.type == pygame.KEYUP:
                # Cancel the motion by adding the opposite of the keydown situation
                if event.key == config.LEFT:
                    self.hero.changespeed(3, 0)
                elif event.key == config.RIGHT:
                    self.hero.changespeed(-3, 0)
                elif event.key == config.UP:
                    self.hero.changespeed(0, 3)
                elif event.key == config.DOWN:
                    self.hero.changespeed(0, -3)

    def die(self):
        self.manager.go_to(DeathScreen())


class DeathScreen(GameState):
    """
    A game state for showing the hero's death.
    """

    def __init__(self):
        super().__init__()

    def draw(self, screen):
        screen.fill(config.BLACK)
        death_text = sn.load_font("Melma.ttf", 32).render(
            "You Died! \n Press any key to try again.", 1, config.RED
        )
        screen.blit(death_text, (200, 350))

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.manager.go_to(TitleScreen())