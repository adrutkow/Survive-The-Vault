import pygame
import perlin_noise

WINDOW = pygame.display.set_mode((1366, 768))
ALPHA_WINDOW = pygame.Surface((1366, 768))
ALPHA_WINDOW.set_alpha(128)
DEFAULT_X = 1366
DEFAULT_Y = 768
CLOCK = pygame.time.Clock()
BLOCKS = pygame.image.load("files/blocks/blocks.png").convert_alpha()
ITEMS = pygame.image.load("files/items/items.png").convert_alpha()
INVENTORY = pygame.image.load("files/misc/inventory.png").convert()
PLAYER_IMAGE = pygame.image.load("files/player/player.png").convert_alpha()
TITLE_SCREEN = pygame.image.load("files/misc/title_screen.png").convert()
CRAFT_MENU = pygame.image.load("files/misc/craft_menu.png").convert()
BUTTONS = pygame.image.load("files/misc/buttons.png").convert()
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
    {"name": "Wood", "is_material": True},                                #0
    {"name": "Stone", "is_material": True},
    {"name": "Sliwka", "is_food": True, "hunger": 5},
    {"name": "Wooden block", "places": 2},
    {"name": "Stone block", "places": 3},
    {"name": "fuckig hoe", "is_tool": True, "is_hoe": True},
    {"name": "rare sliwka", "is_food": True, "hunger": 100},
    {"name": "fuckig sword", "is_tool": True},
    {"name": "blunt", "is_food": True, "hunger": 20},
    {"name": "Bosnian sword", "is_tool": True},
    {"name": "bomba"},                                                     #10
    {"name": "kazakhstan bomba"},
    {"name": "soy"},
    {"name": "one sliwka"},
    {"name": "bendy axe", "is_tool": True, "is_axe": True},
    {"name": "bendy fans"},
    {"name": "Sliwka sword", "is_tool": True}
]

ENTITY_DATA = [
    {"name": "Tree", "top": 4},
    {"name": "Rock"},
    {"name": "Wooden Block", "top": 7},
    {"name": "Stone Block", "top": 9}
]

BLOCK_DATA = [
    {"name": "grass", "walkable": True, "texture":0},
    {"name": "water", "texture":1},
    {"name": "sand", "walkable": True, "texture":2},
    {"name": "farmland", "walkable":True, "texture":10}
]

CRAFT_RECIPES = [
    [[[0, 50], [1, 50]], 5],
    [[[2, 150]], 6],
    [[[0, 50], [1, 50]], 7],
    [[[0, 25]], 3],
    [[[1, 25]], 4],
    [[[0, 100], [1, 100]], 14],
    [[[2, 50], [0,100], [1,100]], 15]
]

# int(abs(config.NOISE((x/30, y/30)) * 255))
