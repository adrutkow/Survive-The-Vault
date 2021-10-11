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
CRAFT_MENU = pygame.image.load("files/misc/craft_menu.png").convert()
SEED = 2131231
OCTAVE = 1
NOISE = perlin_noise.PerlinNoise(OCTAVE, SEED)
ENTITY_TEXTURE_ID = [3, 5, 6, 8]

ENTITY_LOOT_TABLE = [
    [[0, [3, 5], -1], [2, 1, 3], [6, 1, 1000]],
    [[1, [3, 5], -1]],
    [[3, 1, -1]],
    [[4, 1, -1]]
]

ITEM_DATA = [
    {"name": "Wood", "is_material": True},
    {"name": "Stone", "is_material": True},
    {"name": "Sliwka", "is_food": True},
    {"name": "Wooden block", "places": 2},
    {"name": "Stone block", "places": 3},
    {"name": "fuckig hoe", "is_tool": True},
    {"name": "rare sliwka", "is_food": True},
    {"name": "fuckig sword", "is_tool": True},
    {"name": "blunt", "is_food": True},
    {"name": "Bosnian sword", "is_tool": True},
    {"name": "bomba"},
    {"name": "kazakhstan bomba"},
    {"name": "soy"},
    {"name": "one sliwka"}
]

ENTITY_DATA = [
    {"name": "Tree", "top": 4},
    {"name": "Rock"},
    {"name": "Wooden Block", "top": 7},
    {"name": "Stone Block", "top": 9}
]

CRAFT_RECIPES = [
    [[[0, 50], [1, 50]], 5],
    [[[2, 150]], 6],
    [[[0, 50], [1, 50]], 7],
    [[[0, 25]], 3],
    [[[1, 25]], 4]
]

# int(abs(config.NOISE((x/30, y/30)) * 255))
