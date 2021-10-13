import config
import functions
import pygame
import variables
from random import randint


class Game:
    def __init__(self):
        self.world = World()
        self.players = []
        self.npcs = []
        self.buttons = []
        self.buttons.append(Button(4, 1199, 602, 51, 53))
        self.buttons.append(Button(5, 1250, 602, 51, 53))
        self.buttons.append(Button(6, 1300, 602, 51, 53))
        self.npcs.append(Npc())

    def tick(self):
        for i in self.players:
            i.tick()
        for i in self.npcs:
            i.tick()


class World:
    def __init__(self):
        self.chunks = []
        self.time = 0
        self.alpha = 0
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

    def tick(self):
        self.time += 60 * variables.delta_time
        self.draw()

    def draw(self):
        self.alpha = self.time // 400

        if self.alpha > 200:
            self.alpha = 200

        config.ALPHA_WINDOW.set_alpha(self.alpha)
        config.WINDOW.blit(config.ALPHA_WINDOW, (0, 0))
        return



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
        self.hardness = 1
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
        self.speed = 240
        self.offset_x = 1366 / 2 + self.w / 2
        self.offset_y = 768 / 2 + self.h / 2
        self.collision_box = [self.x - self.w / 2, self.y + self.h - 10, 5, 5]
        self.is_harvesting = False
        self.currently_harvesting = None
        self.is_eating = False
        self.bonus = 0
        self.currently_eating = None
        self.progress_bar = ProgressBar(self)
        self.inventory = Inventory(self, [3, 9], 1198, 148)
        self.craft_menu = CraftMenu(self, 1044, 112)
        self.health = 100
        self.hunger = 100
        self.timer = 0
        for y in range(0, 3):
            for x in range(0, 3):
                if x == 1 and y == 1:
                    continue
                self.adjacent_chunks.append(self.world.get_chunk(x - 1, y - 1))

    def tick(self):
        old_timer = self.timer
        self.timer += 1 * variables.delta_time
        if int(self.timer) != int(old_timer):
            if int(self.timer) % 20 == 0:
                self.hunger -= 1
        self.chunk_x, self.chunk_y = functions.get_chunk_coords(self.x, self.y)
        self.movement()
        self.do_harvest()
        self.do_eating()
        self.chunk_check()
        self.draw()

        self.world.tick()

        functions.draw_image(config.INVENTORY, 1198, 112)
        functions.draw_image(config.BUTTONS, 1198, 604)
        self.inventory.draw_items()
        self.craft_menu.tick()
        self.do_hunger()

    def movement(self):
        keys = pygame.key.get_pressed()
        old_x = self.x
        old_y = self.y

        if keys[pygame.K_w]:
            self.y -= self.speed * variables.delta_time
        if keys[pygame.K_s]:
            self.y += self.speed * variables.delta_time
        if keys[pygame.K_a]:
            self.x -= self.speed * variables.delta_time
        if keys[pygame.K_d]:
            self.x += self.speed * variables.delta_time
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

        # Draw the red rectangle thingy
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        if self.craft_menu.active and not self.craft_menu.check_mouse(mouse_x, mouse_y):
            if not self.inventory.check_mouse(mouse_x, mouse_y):
                # This is so stupid
                off_x, off_y = 17, 17
                m_x = self.x % 50
                m_y = self.y % 50
                x = (mouse_x + m_x + off_x) // 50 * 50 - m_x
                y = (mouse_y + m_y + off_y) // 50 * 50 - m_y
                pygame.draw.rect(config.WINDOW, [255, 0, 0], [x - off_x, y - off_y, 50, 50], 2)
        self.progress_bar.draw()
        functions.draw_text("health: " + str(self.health), 0, 0)
        functions.draw_text("hunger: " + str(self.hunger), 0, 20)
        functions.draw_text("time: "+str(self.world.time//60), 0, 40)
        functions.draw_text("alpha: "+str(self.world.alpha), 0, 60)
        functions.draw_text("fps: "+str(config.CLOCK.get_fps())[:4], 0, 80)

    def check_position(self, x, y):
        b_x, b_y = functions.get_block_coords(x, y)
        chunk = self.current_chunk
        block = chunk.blocks[b_y][b_x]

        # is it in same chunk
        if not (self.current_chunk.x == functions.get_chunk_coords(x, y)[0] and self.current_chunk.y ==
                functions.get_chunk_coords(x, y)[1]):
            chunk = self.world.get_chunk(functions.get_chunk_coords(x, y)[0], functions.get_chunk_coords(x, y)[1])
            block = chunk.blocks[b_y][b_x]

        if block.entity is not None:
            return False
        if config.BLOCK_DATA[block.id].get("walkable") is not None:
            return True
        return False

    def harvest(self, entity, bonus=0):
        self.is_harvesting = True
        self.currently_harvesting = entity
        self.progress_bar.active = True
        self.progress_bar.progress = 0
        self.progress_bar.max_progress = entity.hardness
        self.bonus = bonus

    def do_harvest(self):
        if not self.is_harvesting:
            return
        self.progress_bar.progress += (1 + self.bonus) * variables.delta_time
        if self.progress_bar.progress >= self.progress_bar.max_progress:
            if self.currently_harvesting.block is not None:
                functions.get_loot_from_entity(self.currently_harvesting.id, self.inventory)
                self.currently_harvesting.block.entity = None
                self.is_harvesting = False
                self.progress_bar.reset()

    def eat(self):
        self.is_eating = True
        self.currently_eating = self.inventory.inventory[self.inventory.selected[1]][self.inventory.selected[0]].id
        self.progress_bar.active = True
        self.progress_bar.progress = 0
        self.progress_bar.max_progress = 0.5

    def do_eating(self):
        if not self.is_eating:
            return
        self.progress_bar.progress += 1 * variables.delta_time
        if self.progress_bar.progress >= self.progress_bar.max_progress:
            self.hunger += config.ITEM_DATA[self.currently_eating]["hunger"]
            self.hunger = 100 if self.hunger > 100 else self.hunger
            self.inventory.remove_item(self.currently_eating, 1)
            self.progress_bar.reset()
            self.is_eating = False
            self.currently_eating = None


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

    def do_hunger(self):
        if self.timer % 3 == 0:
            if self.hunger <= 0:
                self.health -= 1
            else:
                self.hunger -= 1


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
    def __init__(self, id, x, y, w, h, text="", owner=None):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.active = True
        self.text = text
        self.owner = owner

    def on_click(self):
        # Start game button
        if self.id == 0:
            functions.initialize()
            variables.client.scene = 99
        # Craft button
        if self.id == 1:
            self.owner.craft()
        # Previous craft button
        if self.id == 2:
            self.owner.previous_craft()
        # Next craft button
        if self.id == 3:
            self.owner.next_craft()
        # Toggle craft button
        if self.id == 4:
            variables.player.craft_menu.active = not variables.player.craft_menu.active
            print(variables.player.craft_menu.active)


    def is_clicked(self, x, y):
        mouse_click = pygame.mouse.get_pressed()
        if mouse_click[0]:
            if self.x < x < self.x + self.w and self.y < y < self.y + self.h:
                return True

    def tick(self):
        if not self.active:
            return
        if self.owner == variables.player.craft_menu and not variables.player.craft_menu.active:
            return
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
        self.current_buttons.append(Button(0, 0, 0, 1366, 768))

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
        self.is_axe = config.ITEM_DATA[id].get("is_axe")
        self.is_hoe = config.ITEM_DATA[id].get("is_hoe")
        self.places = config.ITEM_DATA[id].get("places")

    def use(self):
        if self.places is not None:
            x = variables.player.x + pygame.mouse.get_pos()[0] - 1366 / 2
            y = variables.player.y + pygame.mouse.get_pos()[1] - 768 / 2
            if functions.place_block(x, y, self.places):
                variables.player.inventory.remove_item(self.id, 1)
        if self.is_food is not None:
            variables.player.eat()
        if self.is_hoe is not None:
            functions.make_farmland()


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

    def add_item(self, item_id, amount):
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is None:
                    continue
                if self.inventory[y][x].id == item_id:
                    self.inventory[y][x].amount += amount
                    return
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is None:
                    self.inventory[y][x] = Item(item_id, amount)
                    return

    def remove_item(self, item_id, amount):
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is None:
                    continue
                if self.inventory[y][x].id == item_id:
                    self.inventory[y][x].amount -= amount
                    if self.inventory[y][x].amount <= 0:
                        self.inventory[y][x] = None


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

    def check_if_has_items(self, id, amount):
        for y in range(0, self.layout[1]):
            for x in range(0, self.layout[0]):
                if self.inventory[y][x] is None:
                    continue
                if self.inventory[y][x].id == id:
                    if self.inventory[y][x].amount >= amount:
                        return True
        return False

    def get_selected_item(self):
        if self.selected is None:
            return None
        if self.inventory[self.selected[1]][self.selected[0]] is None:
            return None
        return self.inventory[self.selected[1]][self.selected[0]]


class CraftMenu:
    def __init__(self, player, x, y):
        self.x = x
        self.y = y
        self.w = 152
        self.h = 488
        self.owner = player
        self.active = True
        self.index = 0
        self.max_index = len(config.CRAFT_RECIPES)
        self.buttons = []
        self.buttons.append(Button(1, self.x + 17, self.y + 434, 118, 37, owner=self))
        self.buttons.append(Button(2, self.x + 7, self.y + 54, 42, 50, owner=self))
        self.buttons.append(Button(3, self.x + 103, self.y + 54, 42, 50, owner=self))
        self.owner.game.buttons.extend(self.buttons)

    def draw(self):
        current_item = config.CRAFT_RECIPES[self.index][1]
        functions.draw_image(config.CRAFT_MENU, self.x, self.y)
        functions.draw_image(functions.get_item(current_item), self.x + 51, self.y + 54)
        functions.draw_text(config.ITEM_DATA[current_item]["name"], 7 + self.x, 106 + self.y)
        for i in range(0, len(config.CRAFT_RECIPES[self.index][0])):
            t = config.CRAFT_RECIPES[self.index][0][i]
            item_id = t[0]
            item_amount = t[1]
            functions.draw_image(functions.get_item(item_id), self.x + 6, self.y + 134 + i*50 + i*2)
            functions.draw_text(config.ITEM_DATA[item_id]["name"]+" x"+str(item_amount), 60 + self.x, 158 + i * 50 + self.y, size=15)


    def tick(self):
        if not self.active:
            return
        self.draw()

    def check_mouse(self, mouse_x, mouse_y):
        x = self.x
        y = self.y
        return x < mouse_x < x + self.w and y < mouse_y < y + self.h

    def next_craft(self):
        self.index += 1
        if self.index >= self.max_index:
            self.index = 0

    def previous_craft(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.max_index - 1

    def craft(self):
        if self.can_craft():
            for i in range(0, len(config.CRAFT_RECIPES[self.index][0])):
                t = config.CRAFT_RECIPES[self.index][0][i]
                item_id = t[0]
                item_amount = t[1]
                self.owner.inventory.remove_item(item_id, item_amount)
            self.owner.inventory.add_item(config.CRAFT_RECIPES[self.index][1], 1)


    def can_craft(self):
        current_item = config.CRAFT_RECIPES[self.index][1]
        for i in range(0, len(config.CRAFT_RECIPES[self.index][0])):
            t = config.CRAFT_RECIPES[self.index][0][i]
            item_id = t[0]
            item_amount = t[1]
            if not self.owner.inventory.check_if_has_items(item_id, item_amount):
                return False
        return True


class Npc:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 40
        self.h = 70
        self.id = 0
        self.speed = 50

    def tick(self):
        self.draw()

    def draw(self):
        e_x, e_y = self.x - variables.player.x + 1366/2, self.y - variables.player.y + 768/2
        functions.draw_image(config.BOB, e_x, e_y)

    def is_mouse_over(self, x, y):
        e_x, e_y = self.x - variables.player.x + 1366 / 2, self.y - variables.player.y + 768 / 2
        return e_x < x < e_x + self.w and e_y < y < e_y + self.h

