import config
import functions
import pygame
import variables
from random import randint


class Game:
    def __init__(self):
        self.world = World()
        self.players = []

    def tick(self):
        for i in self.players:
            i.tick()


class World:
    def __init__(self):
        self.chunks = []
        self.entities = []
        for y in range(-2, 2):
            for x in range(-2, 2):
                self.chunks.append(Chunk(x, y))

    def get_chunk(self, x, y):
        for i in self.chunks:
            if i.x == x and i.y == y:
                return i
        new_chunk = Chunk(x, y)
        self.chunks.append(new_chunk)
        return new_chunk

    def get_block(self, x, y):
        chunk = self.get_chunk(functions.get_chunk_coords(x, y)[0], functions.get_chunk_coords(x, y)[1])
        bx, by = functions.get_block_coords(x, y)
        return chunk.blocks[by][bx]


class Chunk:
    def __init__(self, x, y):
        self.blocks = []
        self.size = 16
        self.x = x
        self.y = y
        self.generate()

    def generate(self):
        for y in range(0, self.size):
            temp_blocks = []
            for x in range(0, self.size):
                noise_value = config.NOISE(((x + self.x * 16) / 30, (y + self.y * 16) / 30))
                if noise_value >= 0:
                    b = 0
                else:
                    if noise_value > -0.1:
                        b = 2
                    else:
                        b = 1
                temp_blocks.append(Block(b, self.x * self.size + x, self.y * self.size + y))

                if b == 0:
                    r = randint(0, 20)
                    if r == 0:
                        temp_blocks[-1].entity = Entity(0, self.x * self.size + x, self.y * self.size + y, temp_blocks[-1])
                    if r == 1:
                        temp_blocks[-1].entity = Entity(1, self.x * self.size + x, self.y * self.size + y, temp_blocks[-1])

            self.blocks.append(temp_blocks)


class Block:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.entity = None


class Entity:
    def __init__(self, id, x, y, block=None):
        self.id = id
        self.x = x
        self.y = y
        self.harvestable = True
        self.resources = None
        self.hardness = 60
        self.block = block

    def draw(self, x, y):
        if config.ENTITY_DATA[self.id].get("top") is not None:
            functions.draw_image(functions.get_block(config.ENTITY_DATA[self.id].get("top")), x, y - 49)
        functions.draw_image(functions.get_block(config.ENTITY_TEXTURE_ID[self.id]), x, y)


class Player:
    def __init__(self, game):
        self.x = 1366 / 2
        self.y = 768 / 2
        self.w = 30
        self.h = 50
        self.chunk_x = 0
        self.chunk_y = 0
        self.game = game
        self.world = game.world
        self.current_chunk = self.world.get_chunk(self.chunk_x, self.chunk_y)
        self.adjacent_chunks = []
        self.speed = 5
        self.offset_x = 1366 / 2 + self.w / 2
        self.offset_y = 768 / 2 + self.h / 2
        self.collision_box = [self.x - self.w / 2, self.y + self.h - 10, 5, 5]
        self.is_harvesting = False
        self.currently_harvesting = None
        self.progress_bar = ProgressBar(self)
        self.inventory = Inventory(self, [3, 9], 1198, 148)
        for y in range(0, 3):
            for x in range(0, 3):
                if x == 1 and y == 1:
                    continue
                self.adjacent_chunks.append(self.world.get_chunk(x - 1, y - 1))

    def tick(self):
        self.chunk_x, self.chunk_y = functions.get_chunk_coords(self.x, self.y)
        self.movement()
        functions.mouse()
        self.do_harvest()
        self.chunk_check()
        self.draw()
        functions.draw_image(config.INVENTORY, 1198, 112)
        self.inventory.draw_items()

    def movement(self):
        keys = pygame.key.get_pressed()
        old_x = self.x
        old_y = self.y

        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_SPACE]:
            print("pos", self.x, self.y, "chunk", functions.get_chunk_coords(self.x, self.y))

        if not self.check_position(self.x, old_y):
            self.x = old_x

        if not self.check_position(old_x, self.y):
            self.y = old_y

        # Check if moved
        moved = False
        if self.x != old_x or self.y != old_y:
            moved = True

        if moved:
            if self.is_harvesting:
                self.is_harvesting = False
                self.progress_bar.reset()

    def draw(self):
        functions.draw_chunk(self.current_chunk, self)
        for i in self.adjacent_chunks:
            functions.draw_chunk(i, self)
        pygame.draw.rect(config.WINDOW, (255, 0, 0), [1366 / 2, 768 / 2, 2, 2])
        functions.draw_image(config.PLAYER_IMAGE, 1366 / 2 - self.w / 2, 768 / 2 - self.h)
        self.progress_bar.draw()

    def check_position(self, x, y):
        return True
        b_x, b_y = functions.get_block_coords(x, y)
        chunk = self.current_chunk

        # is it in same chunk
        if not (self.current_chunk.x == functions.get_chunk_coords(x, y)[0] and self.current_chunk.y ==
                functions.get_chunk_coords(x, y)[1]):
            chunk = self.world.get_chunk(functions.get_chunk_coords(x, y)[0], functions.get_chunk_coords(x, y)[1])

        if chunk.blocks[b_y][b_x].entity is not None:
            return False
        if chunk.blocks[b_y][b_x].id == 0:
            return True

        return False

    def harvest(self, entity):
        self.is_harvesting = True
        self.currently_harvesting = entity
        self.progress_bar.active = True
        self.progress_bar.progress = 0
        self.progress_bar.max_progress = entity.hardness

    def do_harvest(self):
        if not self.is_harvesting:
            return
        self.progress_bar.progress += 1
        if self.progress_bar.progress >= self.progress_bar.max_progress:
            if self.currently_harvesting.block is not None:
                functions.get_loot_from_entity(self.currently_harvesting.id, self.inventory)
                self.currently_harvesting.block.entity = None
                self.is_harvesting = False
                self.progress_bar.reset()

    def chunk_check(self):
        """Checks if the player changed chunks"""
        if self.chunk_x != functions.get_chunk_coords(self.x, self.y)[0] or self.chunk_y != \
                functions.get_chunk_coords(self.x, self.y)[1]:
            print("changed chunk")
            self.chunk_x, self.chunk_y = functions.get_chunk_coords(self.x, self.y)
            self.current_chunk = self.world.get_chunk(self.chunk_x, self.chunk_y)
            block_x, block_y = functions.get_block_coords(self.x, self.y)
            self.adjacent_chunks = []
            for y in range(-1, 2):
                for x in range(-1, 2):
                    if x == 0 and y == 0:
                        continue
                    self.adjacent_chunks.append(
                        self.world.get_chunk(self.current_chunk.x + x, self.current_chunk.y + y))


class Client:
    def __init__(self):
        self.scene = 0
        self.scenes = [MainMenu(), variables.game]

    def tick(self):
        if self.scene == 99:
            variables.game.tick()
            return
        self.scenes[self.scene].tick()


class Button:
    def __init__(self, scene, id, x, y, w, h, text=""):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def on_click(self):
        # Start game button
        if self.id == 0:
            functions.initialize()
            variables.client.scene = 99

    def is_clicked(self, x, y):
        mouse_click = pygame.mouse.get_pressed()
        if mouse_click[0]:
            if self.x < x < self.x + self.w and self.y < y < self.y + self.h:
                return True

    def tick(self):
        mouse = pygame.mouse.get_pos()
        if self.is_clicked(mouse[0], mouse[1]):
            self.on_click()


class Scene:
    def __init__(self):
        self.id = 0
        self.current_buttons = []


class MainMenu(Scene):
    def __init__(self):
        super(MainMenu, self).__init__()
        self.current_buttons.append(Button(self, 0, 0, 0, 1366, 768))

    def tick(self):
        for i in self.current_buttons:
            i.tick()
        functions.draw_image(config.TITLE_SCREEN, 0, 0)


class Item:
    def __init__(self, id, amount=0):
        self.id = id
        self.amount = amount
        self.name = config.ITEM_DATA[id].get("name")
        self.is_tool = config.ITEM_DATA[id].get("is_tool")
        self.is_food = config.ITEM_DATA[id].get("is_food")
        self.is_material = config.ITEM_DATA[id].get("is_material")
        self.places = config.ITEM_DATA[id].get("places")

    def use(self):
        if self.places is not None:
            x = variables.player.x + pygame.mouse.get_pos()[0] - 1366 / 2
            y = variables.player.y + pygame.mouse.get_pos()[1] - 768 / 2
            functions.place_block(x, y, self.places)


class ProgressBar:
    def __init__(self, owner):
        self.owner = owner
        self.progress = 1
        self.max_progress = 100
        self.w = 60
        self.h = 20
        self.active = False

    def draw(self):
        if not self.active:
            return
        x = self.owner.x - variables.player.x + 1366 / 2
        y = self.owner.y - variables.player.y + 768 / 2
        pygame.draw.rect(config.WINDOW, (255, 0, 0), (x - self.w/2, y - 80, self.w // (self.max_progress/self.progress), self.h))
        pygame.draw.rect(config.WINDOW, (0, 0, 0), (x - self.w/2, y - 80, self.w, self.h), 3)

    def reset(self):
        self.active = False
        self.progress = 1


class Inventory:
    def __init__(self, owner, layout, x, y):
        self.owner = owner
        self.layout = layout
        self.inventory = []
        self.selected = None
        self.is_active = True
        self.generate_layout()
        self.x = x
        self.y = y

    def generate_layout(self):
        for i in range(0, self.layout[1]):
            arr = [None]*self.layout[0]
            self.inventory.append(arr.copy())
        for i in self.inventory:
            print(i)

    def draw_items(self, pos_x=0, pos_y=0):
        pos_x = self.x
        pos_y = self.y
        if not self.is_active:
            return
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is not None:
                    item_id = self.inventory[y][x].id
                    functions.draw_image(functions.get_item(item_id), pos_x + x*50, pos_y + y*50)
                    functions.draw_text(str(self.inventory[y][x].amount), pos_x + x*50+5, pos_y + y*50+30,color=(255,255,255))
        if self.selected is not None:
            pygame.draw.rect(config.WINDOW, (0,255,0), (self.x+self.selected[0]*50+2, self.y+self.selected[1]*50+2, 49, 49), 2)

    def add_item(self, item):
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is None:
                    continue
                if self.inventory[y][x].id == item.id:
                    self.inventory[y][x].amount += item.amount
                    return
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is None:
                    self.inventory[y][x] = item
                    return

    def check_if_clicked(self):
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        x = self.x
        y = self.y

        if self.check_mouse(mouse_x, mouse_y):
            inv_x = (mouse_x - x) // 50
            inv_y = (mouse_y - y) // 50

            return inv_x,inv_y
        return False

    def check_mouse(self, mouse_x, mouse_y):
        x = self.x
        y = self.y
        return x < mouse_x < x + self.layout[0] * 50 and y < mouse_y < y + self.layout[1] * 50