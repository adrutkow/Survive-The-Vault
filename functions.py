from random import randint

import config
import pygame
import variables
import classes
import pickle


def create_client():
    variables.client = classes.Client()


def initialize():
    variables.game = classes.Game()
    variables.player = classes.Player(variables.game)
    variables.game.players.append(variables.player)


def draw_image(image, x, y):
    window = config.WINDOW
    scale_x = window.get_width() / config.DEFAULT_X
    scale_y = window.get_height() / config.DEFAULT_Y
    window.blit(pygame.transform.scale(image, (int(image.get_width() * scale_x), int(image.get_height() * scale_y))),
                (x * scale_x, y * scale_y))


def draw_text(text, x, y, size=20, color=(0, 0, 0)):
    font = pygame.font.SysFont("Arial", size)
    test = font.render(str(text), True, color)
    config.WINDOW.blit(test, (x, y))


def get_block(id):
    return config.BLOCKS.subsurface([(id % 6) * 50, (int(id / 6)) * 50, 50, 50])


def get_item(id):
    return config.ITEMS.subsurface([(id % 8) * 50, (int(id / 8)), 50, 50])


def draw_chunk(chunk, player):
    for y in range(0, 16):
        for x in range(0, 16):
            pos_x = x * 50 + chunk.x * 16 * 50 - player.x + 1366 / 2
            pos_y = y * 50 + chunk.y * 16 * 50 - player.y + 768 / 2

            if pos_x < -60 or pos_x > 1366 or pos_y < -60 or pos_y > 850:
                continue

            draw_image(get_block(chunk.blocks[y][x].id), pos_x, pos_y)
            if chunk.blocks[y][x].entity is not None:
                chunk.blocks[y][x].entity.draw(pos_x, pos_y)


def get_chunk_coords(x, y):
    chunk_x = int(x / (50 * 16))
    chunk_y = int(y / (50 * 16))
    if x < 0:
        chunk_x -= 1
    if y < 0:
        chunk_y -= 1
    return chunk_x, chunk_y


def get_block_coords(x, y):
    """Returns coordinates of a block inside a chunk from world coordinates"""
    block_x = int((x % (50 * 16)) / 50)
    block_y = int((y % (50 * 16)) / 50)
    return block_x, block_y


def handle_inputs():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
        if e.type == pygame.MOUSEBUTTONDOWN:
            world = variables.game.world
            player = variables.player
            mouse_x = pygame.mouse.get_pos()[0] - 1366 / 2
            mouse_y = pygame.mouse.get_pos()[1] - 768 / 2
            # world.get_block(player.x + mouse_x, player.y + mouse_y).id = 5

    keys = pygame.key.get_pressed()

    if keys[pygame.K_1]:
        save_game(variables.game)
        print("saved game")

    if keys[pygame.K_2]:
        load_game()
        print("loaded game")


def mouse():
    player = variables.player
    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]

    if not player.inventory.check_mouse(mouse_x, mouse_y):
        # This is so stupid
        off_x, off_y = 17, 17
        m_x = player.x % 50
        m_y = player.y % 50
        x = (mouse_x + m_x + off_x) // 50 * 50 - m_x
        y = (mouse_y + m_y + off_y) // 50 * 50 - m_y

        pygame.draw.rect(config.WINDOW, [255, 0, 0], [x - off_x, y - off_y, 50, 50], 2)

    mouse_click = pygame.mouse.get_pressed(3)

    # Left click
    if mouse_click[0]:
        print(mouse_x, mouse_y)
        if player.inventory.check_if_clicked() != False:
            player.inventory.selected = player.inventory.check_if_clicked()
        else:
            player.inventory.selected = None
        variables.player.inventory.add_item(classes.Item(3, 1))


    # Right click
    if mouse_click[2]:
        mouse_x = pygame.mouse.get_pos()[0] - 1366 / 2
        mouse_y = pygame.mouse.get_pos()[1] - 768 / 2
        block = variables.game.world.get_block(player.x + mouse_x, player.y + mouse_y)
        if block.entity is not None:
            if block.entity.harvestable:
                variables.player.harvest(block.entity)
        if player.inventory.selected is not None:
            selected = player.inventory.selected
            if player.inventory.inventory[selected[1]][selected[0]] is not None:
                player.inventory.inventory[selected[1]][selected[0]].use()


def save_game(game):
    draw_text("saving game...", 0, 0)
    pygame.display.update()
    data = [variables.game, variables.player]
    pickle.dump(data, (open("save_files/savefile0.p", "wb")))


def load_game():
    data = pickle.load(open("save_files/savefile0.p", "rb"))
    variables.game = data[0]
    variables.player = data[1]


def get_loot_from_entity(id, inventory):
    for i in config.ENTITY_LOOT_TABLE[id]:
        if i[2] != -1:
            if randint(0, i[2]) != 0:
                continue
        if type(i[1]) == int:
            amount = i[1]
        else:
            amount = randint(i[1][0], i[1][1])
        inventory.add_item(classes.Item(i[0], amount))


def place_block(x, y, id):
    """Places a block in the world using world coordinates"""
    target_block = variables.player.world.get_block(x, y)
    target_block.entity = classes.Entity(id, target_block.x, target_block.y, target_block)