import pygame
import config
import functions
import variables

pygame.font.init()
functions.create_client()
functions.initialize()

while True:
    variables.delta_time = config.CLOCK.tick(60) / 1000
    functions.handle_inputs()
    variables.client.tick()
    pygame.display.update()
