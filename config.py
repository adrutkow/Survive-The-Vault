import pygame
import perlin_noise


WINDOW = pygame.display.set_mode((1366, 768))
DEFAULT_X = 1366
DEFAULT_Y = 768
CLOCK = pygame.time.Clock()
BLOCKS = pygame.image.load("files/blocks/blocks.png").convert_alpha()
ITEMS = pygame.image.load("files/items/items.png").convert_alpha()
INVENTORY = pygame.image.load("files/misc/inventory.png").convert()
PLAYER_IMAGE = pygame.image.load("files/player/player.png").convert_alpha()
TITLE_SCREEN = pygame.image.load("files/misc/title_screen.png").convert()
SEED = 2131231
OCTAVE = 1
NOISE = perlin_noise.PerlinNoise(OCTAVE, SEED)
ENTITY_TEXTURE_ID = [3, 5, 6, 8]


ENTITY_LOOT_TABLE = [
    [[0, [3,5], -1], [2, 1, 3]],
    [[1, [3,5], -1]],
    [[3, 1, -1]],
    [[4, 1, -1]]
]

ITEM_DATA = [
    {"name": "Wood", "is_material": True},
    {"name": "Stone", "is_material": True},
    {"name": "Apple", "is_food": True},
    {"name": "Wooden block", "places": 2},
    {"name": "Stone block", "places": 3}
]

ENTITY_DATA =[
    {"name": "Tree", "top":4},
    {"name": "Rock"},
    {"name": "Wooden Block", "top":7},
    {"name": "Stone Block", "top": 9}
]

# int(abs(config.NOISE((x/30, y/30)) * 255))
