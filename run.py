"""
Run the game.
"""
import os
import pygame
import logging
import config
import spritenames as sn
import time
import rooms

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pygame.init()

HP_FONT = pygame.font.Font(os.path.join('Fonts', 'BLKCHCRY.TTF'), 32)

screen = pygame.display.set_mode(config.SCREEN_RESOLUTION)
background = sn.create_background(sn.load('background.png'))

clock = pygame.time.Clock()

all_sprites_list = pygame.sprite.Group()

Hero = sn.Hero()
all_sprites_list.add(Hero)
#Vars for the timer
displayTime = 0
elapsed_time = time.strftime('%M:%S', time.gmtime(displayTime))

current_room = rooms.Room_01()

done = False
while not done:
    #TODO: Make the background move instead of the HeroSprite. Watch videos of other games, the Hero is always centered
    current_room.draw(screen)

    # Blit HUD
    Hero_hp = HP_FONT.render("HP: {0}".format(Hero.hp), 1, config.WHITE)
    screen.blit(Hero_hp, (0, 0))
    #elapsed time of play
    elapsed_time_display = HP_FONT.render("Elapsed Time: {0}".format(elapsed_time), 1, config.WHITE)
    screen.blit(elapsed_time_display,(600,0))

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.KEYDOWN:
            # Create the motion by changing the Hero's speed vector
            if event.key == config.LEFT:
                logger.debug("[LEFT] key pushed")
                Hero.changespeed(-3, 0)
            elif event.key == config.RIGHT:
                logger.debug("[RIGHT] key pushed")
                Hero.changespeed(3, 0)
            elif event.key == config.UP:
                logger.debug("[UP] key pushed")
                Hero.changespeed(0, -3)  # Backwards because computer coords start in top left
            elif event.key == config.DOWN:
                logger.debug("[DOWN] key pushed")
                Hero.changespeed(0, 3)  # Backwards because computer coords start in top left

        elif event.type == pygame.KEYUP:
            # Cancel the motion by adding the opposite of the keydown situation
            if event.key == config.LEFT:
                logger.debug("[LEFT] key released")
                Hero.changespeed(3, 0)
            elif event.key == config.RIGHT:
                logger.debug("[RIGHT] key released")
                Hero.changespeed(-3, 0)
            elif event.key == config.UP:
                logger.debug("[UP] key released")
                Hero.changespeed(0, 3)
            elif event.key == config.DOWN:
                logger.debug("[DOWN] key released")
                Hero.changespeed(0, -3)

    Hero.move(current_room.block_list)
    all_sprites_list.draw(screen)

    pygame.display.flip()
    clock.tick(60)
    #updates the timer after each run of the loop
    displayTime += 1/60
    elapsed_time = time.strftime('%M:%S', time.gmtime(displayTime))
    screen.blit(elapsed_time_display,(600,0))
    if Hero.hp == 0:
        you_lose = HP_FONT.render("You lose", 1, (255,0,0))
        screen.blit(you_lose,(400,300))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        quit()
