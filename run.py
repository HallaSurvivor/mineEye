"""
Run the game.
"""
import pygame
import config
import spritenames as sn


pygame.init()

screen = pygame.display.set_mode(config.SCREEN_RESOLUTION)

background = sn.create_background(sn.load('background.png'))

x = 0
y = 0

clock = pygame.time.Clock()

done = False
while not done:
    #TODO: Make the background move instead of the HeroSprite. Watch videos of other games, the Hero is always centered
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP] or pressed[pygame.K_w]:
        y -= 3
    if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
        y += 3
    if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
        x -= 3
    if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
        x += 3
    if pressed[pygame.K_SPACE]:
        y = 0
        x = 0

    screen.blit(sn.load('herosprite.png'), (x, y))


    pygame.display.flip()
    clock.tick(60)
