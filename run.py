"""
Run the game.
"""
import os
import pygame
import logging
import config
import spritenames as sn
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pygame.init()

HP_FONT = pygame.font.Font(os.path.join('Fonts', 'BLKCHCRY.TTF'), 32)

screen = pygame.display.set_mode(config.SCREEN_RESOLUTION)
background = sn.create_background(sn.load('background.png'))

clock = pygame.time.Clock()

all_sprites_list = pygame.sprite.Group()
wall_list = pygame.sprite.Group()

wall_1 = sn.Wall(100, 300, sn.load('stone.png'))
wall_list.add(wall_1)
all_sprites_list.add(wall_1)

wall_2 = sn.Wall(400, 700, sn.load('spikes.png'))
wall_2.damage_player = True
wall_list.add(wall_2)
all_sprites_list.add(wall_2)

Hero = sn.Hero()

all_sprites_list.add(Hero)
#Vars for the timer
displayTime = 0
elapsed_time = time.strftime('%M:%S', time.gmtime(displayTime))
done = False
while not done:
    #TODO: Make the background move instead of the HeroSprite. Watch videos of other games, the Hero is always centered

    screen.blit(background, (0, 0))

    Hero_hp = HP_FONT.render("HP: {0}".format(Hero.hp), 1, config.WHITE)
    screen.blit(Hero_hp, (0, 0))
    #elapsed time of play
    elapsed_time_display = HP_FONT.render("Elapsed Time: {0}".format(elapsed_time), 1, config.WHITE)
    screen.blit(elapsed_time_display,(600,0))









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

    Hero.move(wall_list)
    all_sprites_list.draw(screen)

    pygame.display.flip()
    clock.tick(60)
    #updates the timer after each run of the loop
    displayTime += 1/60
    print(displayTime)
    elapsed_time = time.strftime('%M:%S', time.gmtime(displayTime))
    screen.blit(elapsed_time_display,(600,0))