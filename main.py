import pygame
import config
import functions
import variables

pygame.font.init()
functions.create_client()
functions.initialize()

while True:
    functions.handle_inputs()
    variables.client.tick()
    functions.mouse()
    config.CLOCK.tick(60)
    pygame.display.update()