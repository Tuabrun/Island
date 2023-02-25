import pygame
from pygame.locals import *

from load_image import load_image
from button import Button
from world import World
from save_game import save_game
import creatures
from inventory import HotBar
from inventory import PopUpWindow
from file_directory import file_directory
from print_text import print_text

FPS = 60
SPEED = 3
RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"
RIGHT_UP = "right_up"
RIGHT_DOWN = "right_down"
LEFT_UP = "left_up"
LEFT_DOWN = "left_down"


def motion(direction, camera, hero_pos, step_counter):
    if direction in [RIGHT, DOWN]:
        camera -= SPEED
        hero_pos += SPEED
    if direction in [LEFT, UP]:
        camera += SPEED
        hero_pos -= SPEED
    step_counter += 1
    return camera, hero_pos, step_counter


# класс для хранения групп спрайтов
class SpriteGroupsForChunks:
    def __init__(self):
        self.chunk_groups = []
        self.object_groups = []
        self.water_tile_groups = []
        self.for_extraction_with_axe_groups = []
        self.for_extraction_with_pickaxe_groups = []
        # каждая группа спрайтов повторяется 9 раз и передаётся в соответствующий массив
        # далее я поясню зачем это нужно
        for _ in range(9):
            tiles_group = pygame.sprite.Group()
            water_tiles_group = pygame.sprite.Group()
            objects_group = pygame.sprite.Group()
            for_extraction_with_axe_group = pygame.sprite.Group()
            for_extraction_with_pickaxe_group = pygame.sprite.Group()
            self.chunk_groups.append(tiles_group)
            self.water_tile_groups.append(water_tiles_group)
            self.object_groups.append(objects_group)
            self.for_extraction_with_axe_groups.append(for_extraction_with_axe_group)
            self.for_extraction_with_pickaxe_groups.append(for_extraction_with_pickaxe_group)

    def get_all_sprite_groups(self):
        all_sprite_groups = [self.chunk_groups, self.object_groups, self.water_tile_groups,
                             self.for_extraction_with_axe_groups, self.for_extraction_with_pickaxe_groups]
        return all_sprite_groups

    def get_rendered_sprite_groups(self):
        return [self.chunk_groups, self.object_groups]

    def get_material_sprite_groups(self):
        return [self.water_tile_groups, self.object_groups]

    # метод для отрисовки групп спрайтов. Принимает на вход массив из surface
    # далее названием chunk будет называться surface размером с экран
    def draw(self, chunks):
        for sprite_group in self.get_rendered_sprite_groups():
            for i in range(9):
                sprite_group[i].draw(chunks[i])


def update_chunks(direction, piece, sprite_groups, world, chunks, screen_size=0):
    offset = None
    saved_chunks = None
    camera = None
    hero_pos = None
    if direction == RIGHT and piece == (0, 0.5):
        offset = 1
        saved_chunks = [0, 1, 3, 4, 6, 7]
        camera = 0 - screen_size // 2
        hero_pos = 0
    if direction == LEFT and piece == (0.5, 1):
        offset = -1
        saved_chunks = [1, 2, 4, 5, 7, 8]
        camera = -screen_size + 1 - screen_size // 2
        hero_pos = screen_size - 1
    if direction == UP and piece == (0.5, 1):
        offset = -3
        saved_chunks = list(range(3, 9))
        camera = -screen_size + 1 - screen_size // 2
        hero_pos = screen_size - 1
    if direction == DOWN and piece == (0, 0.5):
        offset = 3
        saved_chunks = list(range(6))
        camera = 0 - screen_size // 2
        hero_pos = 0

    if (direction == RIGHT and piece == (0, 0.5)) or (direction == LEFT and piece == (0.5, 1)) \
            or (direction == UP and piece == (0.5, 1)) or (direction == DOWN and piece == (0, 0.5)):
        sprite_groups_copy = SpriteGroupsForChunks()
        for index in saved_chunks:
            for group_of_sprites in range(len(sprite_groups.get_all_sprite_groups())):
                sprite_groups_copy.get_all_sprite_groups()[group_of_sprites][index] = \
                    sprite_groups.get_all_sprite_groups()[group_of_sprites][index + offset]
        sprite_groups = sprite_groups_copy
    world.update(sprite_groups, direction, piece)
    sprite_groups.draw(chunks)
    if screen_size != 0:
        return sprite_groups, camera, hero_pos
    return sprite_groups


def menu_cycle(screen, click_sound):
    menu_background = load_image('background.jpg')
    start_button = Button(270, 60)
    save_button = Button(290, 60)
    quit_button = Button(135, 60)

    # ограничение списка проверяемых событий для лучшей производительности
    pygame.event.set_allowed([QUIT])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        screen.blit(menu_background, (0, 0))
        new_game = start_button.draw(screen, 810, 340, 'NEW GAME', click_sound, "new_world")
        load_game = save_button.draw(screen, 800, 450, 'LOAD GAME', click_sound, "change_cycle")
        quit_button.draw(screen, 870, 565, 'EXIT', click_sound, "quit")

        if not new_game or not load_game:
            return True

        pygame.display.update()


def game_finish_cycle(screen, true_width, true_height, window_group, stones):
    click_sound = pygame.mixer.Sound(file_directory("data/sounds/click.wav"))
    menu_background = PopUpWindow(window_group, true_width, true_height)
    click_sound.play()
    ok_button = Button(85, 55)

    pygame.event.set_allowed([QUIT])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        screen.blit(menu_background.image, (true_width // 2 - 312, true_height // 2 - 256))
        print_text(screen, true_width // 2 - 256, true_height // 2 - 64, f"you have collected {stones} stones",
                   font_size=20)
        finish = ok_button.draw(screen, true_width // 2 - 43, true_height // 2 + 128, 'OK', click_sound, "change_cycle")
        if not finish:
            return finish
        pygame.display.update()


def game_cycle(screen, width, height, save_number, step_sound):
    sprite_groups = SpriteGroupsForChunks()
    hero_group = pygame.sprite.Group()
    interface_group = pygame.sprite.Group()
    item_group = pygame.sprite.Group()

    info_object = pygame.display.Info()
    true_width = info_object.current_w
    true_height = info_object.current_h

    step_counter = 0
    vol = 0.1

    # ограничение списка проверяемых событий для лучшей производительности
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    clock = pygame.time.Clock()
    counter = -1

    world = World(900, 450, 2, width, height, sprite_groups)
    # координаты персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ
    # пояснение: в игре отрисовываются лишь 9 чанков, и в центральном чанке находится персонаж
    # как раз таки поэтому каждая группа спрайтов повторялатсь 9 раз. Каждой группе спрайтов соответствует свой чанк
    world.load_save(save_number)
    hero_x, hero_y = world.hero_x, world.hero_y
    # присваивание тайлам и объектам соответствующие спрайты
    world.draw()

    # создание чанков
    chunks = []
    for index in range(9):
        chunk = pygame.Surface((width, height)).convert()
        chunk.set_alpha(None)
        chunks.append(chunk)
    # отрисовка спрайтов на этих чанках
    sprite_groups.draw(chunks)
    right_chunk = left_chunk = up_chunk = down_chunk = True
    right_up_chunk = right_down_chunk = left_up_chunk = left_down_chunk = [True, True]

    hot_bar = HotBar(interface_group, true_width, true_height)

    hero = creatures.Hero(hero_group)
    direction_x = direction_y = None
    sprite = target_x = target_y = None

    # координаты центрального чанка на дисплее
    camera_x, camera_y = -hero_x - width // 2, -hero_y - height // 2
    # переменные, отвечающие за движение камеры
    motion_x = motion_y = None

    running = True
    stones = 0
    while running:
        counter = (counter + 1) % 96
        frame_number = counter // 4 + 1

        if target_x is not None and -48 + SPEED + 1 < target_x < 48 - SPEED - 1:
            motion_x = None
        if target_y is not None and -48 + SPEED + 1 < target_y < 48 - SPEED - 1:
            motion_y = None

        if step_counter == 20:
            step_sound.play()
            step_counter += 1
        elif step_counter > 20:
            step_counter = 0

        for event in pygame.event.get():
            # нажатие крестика в правом верхнем углу
            if event.type == pygame.QUIT:
                save_game(save_number, world, hero_x, hero_y)
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(save_number, world, hero_x, hero_y)
                    game_finish_cycle(screen, true_width, true_height, interface_group, stones)
                    return False

                if event.key == pygame.K_d:
                    motion_x = direction_x = RIGHT
                if event.key == pygame.K_a:
                    motion_x = direction_x = LEFT
                if event.key == pygame.K_w:
                    motion_y = direction_y = UP
                if event.key == pygame.K_s:
                    motion_y = direction_y = DOWN

                if event.key == pygame.K_1:
                    hero.what_is_in_hands = "axe"
                if event.key == pygame.K_2:
                    hero.what_is_in_hands = "pickaxe"

                if event.key == pygame.K_f:
                    sprite_inf = hero.find_nearest_sprite(sprite_groups, hero_x, hero_y, width, height)
                    sprite, target_x, target_y = sprite_inf
                    if sprite is None:
                        sprite = target_x = target_y = None

                if event.key == pygame.K_LEFT:
                    if vol > 0.0:
                        vol -= 0.1
                        pygame.mixer.music.set_volume(vol)
                if event.key == pygame.K_RIGHT:
                    if vol < 1.0:
                        vol += 0.1
                        pygame.mixer.music.set_volume(vol)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d and motion_x == RIGHT:
                    motion_x = None
                if event.key == pygame.K_a and motion_x == LEFT:
                    motion_x = None
                if event.key == pygame.K_w and motion_y == UP:
                    motion_y = None
                if event.key == pygame.K_s and motion_y == DOWN:
                    motion_y = None
                if event.key == pygame.K_f:
                    sprite = target_x = target_y = None
                    motion_x = motion_y = None

        stop_motion = hero.check_collision(sprite_groups.get_material_sprite_groups(), motion_x, motion_y,
                                           hero_x, hero_y, width, height)

        if target_x is not None and stop_motion[0] != RIGHT and target_x > 44:
            camera_x, hero_x, step_counter = motion(RIGHT, camera_x, hero_x, step_counter)
            stop_motion[0] = RIGHT
            motion_x = RIGHT
            direction_x = RIGHT
            target_x -= SPEED
        if target_x is not None and stop_motion[0] != LEFT and target_x < -44:
            camera_x, hero_x, step_counter = motion(LEFT, camera_x, hero_x, step_counter)
            stop_motion[0] = LEFT
            motion_x = LEFT
            direction_x = LEFT
            target_x += SPEED
        if target_y is not None and stop_motion[1] != UP and target_y < -44:
            camera_y, hero_y, step_counter = motion(UP, camera_y, hero_y, step_counter)
            stop_motion[1] = UP
            motion_y = UP
            direction_y = UP
            target_y += SPEED
        if target_y is not None and stop_motion[1] != DOWN and target_y > 44:
            camera_y, hero_y, step_counter = motion(DOWN, camera_y, hero_y, step_counter)
            stop_motion[1] = DOWN
            motion_y = DOWN
            direction_y = DOWN
            target_y -= SPEED

        if motion_x == RIGHT and stop_motion[0] != RIGHT:
            camera_x, hero_x, step_counter = motion(RIGHT, camera_x, hero_x, step_counter)
        if motion_x == LEFT and stop_motion[0] != LEFT:
            camera_x, hero_x, step_counter = motion(LEFT, camera_x, hero_x, step_counter)
        if motion_y == UP and stop_motion[1] != UP:
            camera_y, hero_y, step_counter = motion(UP, camera_y, hero_y, step_counter)
        if motion_y == DOWN and stop_motion[1] != DOWN:
            camera_y, hero_y, step_counter = motion(DOWN, camera_y, hero_y, step_counter)

        action = "run"
        if motion_x is None:
            direction = direction_y
        else:
            direction = direction_x

        if sprite is not None and sprite.check_collision(hero_group, width, height):
            if hero.what_is_in_hands == "pickaxe":
                action = "mine"
            if hero.what_is_in_hands == "axe":
                action = "cut_down"
            direction = direction_x
            if counter in [31, 63, 95] and action != "cut_down":
                world.object_grids, is_destroyed = sprite.update(world.object_grids)
                if is_destroyed:
                    stones += 1
                    hero.update_inventory(item_group, hot_bar, sprite.type)
                    sprite_inf = hero.find_nearest_sprite(sprite_groups, hero_x, hero_y, width, height)
                    sprite, target_x, target_y = sprite_inf
                    if sprite is None:
                        sprite = target_x = target_y = None
                sprite_groups.draw(chunks)

        if motion_y is None and motion_x is None and action == "run":
            frame_number = 0
        hero.update(action, direction, frame_number)

        #
        if camera_x + width // 2 <= -width:
            if not up_chunk:
                sprite_groups = update_chunks(UP, (0, 0.5), sprite_groups, world, chunks)
            if not down_chunk:
                sprite_groups = update_chunks(DOWN, (0.5, 1), sprite_groups, world, chunks)
            if not right_up_chunk[0]:
                sprite_groups = update_chunks(RIGHT_UP, (0, 0.5), sprite_groups, world, chunks)
            if not right_up_chunk[1]:
                sprite_groups = update_chunks(RIGHT_UP, (0.5, 1), sprite_groups, world, chunks)
            if not right_down_chunk[0]:
                sprite_groups = update_chunks(RIGHT_DOWN, (0, 0.5), sprite_groups, world, chunks)
            if not right_down_chunk[1]:
                sprite_groups = update_chunks(RIGHT_DOWN, (0.5, 1), sprite_groups, world, chunks)
            sprite_groups, camera_x, hero_x = update_chunks(RIGHT, (0, 0.5), sprite_groups, world, chunks, width)
            right_chunk = False
            right_up_chunk = right_down_chunk = [False, False]
            left_chunk = up_chunk = down_chunk = True
            left_up_chunk = left_down_chunk = [True, True]
        if camera_x + width // 2 > 0:
            if not up_chunk:
                sprite_groups = update_chunks(UP, (0, 0.5), sprite_groups, world, chunks)
            if not down_chunk:
                sprite_groups = update_chunks(DOWN, (0.5, 1), sprite_groups, world, chunks)
            if not left_up_chunk[0]:
                sprite_groups = update_chunks(LEFT_UP, (0.5, 1), sprite_groups, world, chunks)
            if not left_up_chunk[1]:
                sprite_groups = update_chunks(LEFT_UP, (0, 0.5), sprite_groups, world, chunks)
            if not left_down_chunk[0]:
                sprite_groups = update_chunks(LEFT_DOWN, (0.5, 1), sprite_groups, world, chunks)
            if not left_down_chunk[1]:
                sprite_groups = update_chunks(LEFT_DOWN, (0, 0.5), sprite_groups, world, chunks)
            sprite_groups, camera_x, hero_x = update_chunks(LEFT, (0.5, 1), sprite_groups, world, chunks, width)
            left_chunk = False
            left_up_chunk = left_down_chunk = [False, False]
            right_chunk = up_chunk = down_chunk = True
            right_up_chunk = right_down_chunk = [True, True]
        if camera_y + height // 2 >= 0:
            if not right_chunk:
                sprite_groups = update_chunks(RIGHT, (0.5, 1), sprite_groups, world, chunks)
            if not left_chunk:
                sprite_groups = update_chunks(LEFT, (0, 0.5), sprite_groups, world, chunks)
            if not right_up_chunk[0]:
                sprite_groups = update_chunks(RIGHT_UP, (0, 0.5), sprite_groups, world, chunks)
            if not right_up_chunk[1]:
                sprite_groups = update_chunks(RIGHT_UP, (0.5, 1), sprite_groups, world, chunks)
            if not left_up_chunk[0]:
                sprite_groups = update_chunks(LEFT_UP, (0.5, 1), sprite_groups, world, chunks)
            if not left_up_chunk[1]:
                sprite_groups = update_chunks(LEFT_UP, (0, 0.5), sprite_groups, world, chunks)
            sprite_groups, camera_y, hero_y = update_chunks(UP, (0.5, 1), sprite_groups, world, chunks, height)
            up_chunk = False
            right_up_chunk = left_up_chunk = [False, False]
            right_chunk = left_chunk = down_chunk = True
            right_down_chunk = left_down_chunk = [True, True]
        if camera_y + height // 2 <= -height:
            if not right_chunk:
                sprite_groups = update_chunks(RIGHT, (0.5, 1), sprite_groups, world, chunks)
            if not left_chunk:
                sprite_groups = update_chunks(LEFT, (0, 0.5), sprite_groups, world, chunks)
            if not right_down_chunk[0]:
                sprite_groups = update_chunks(RIGHT_DOWN, (0, 0.5), sprite_groups, world, chunks)
            if not right_down_chunk[1]:
                sprite_groups = update_chunks(RIGHT_DOWN, (0.5, 1), sprite_groups, world, chunks)
            if not left_down_chunk[0]:
                sprite_groups = update_chunks(LEFT_DOWN, (0.5, 1), sprite_groups, world, chunks)
            if not left_down_chunk[1]:
                sprite_groups = update_chunks(LEFT_DOWN, (0, 0.5), sprite_groups, world, chunks)
            sprite_groups, camera_y, hero_y = update_chunks(DOWN, (0, 0.5), sprite_groups, world, chunks, height)
            down_chunk = False
            right_down_chunk = left_down_chunk = [False, False]
            right_chunk = left_chunk = up_chunk = True
            right_up_chunk = left_up_chunk = [True, True]

        if camera_x + width // 2 < -width * 0.25 and not right_chunk:
            sprite_groups = update_chunks(RIGHT, (0.5, 1), sprite_groups, world, chunks)
            right_chunk = True
        if camera_x + width // 2 > -width * 0.75 and not left_chunk:
            sprite_groups = update_chunks(LEFT, (0, 0.5), sprite_groups, world, chunks)
            left_chunk = True
            print(LEFT)
        if camera_y + height // 2 > -height * 0.75 and not up_chunk:
            sprite_groups = update_chunks(UP, (0, 0.5), sprite_groups, world, chunks)
            up_chunk = True
        if camera_y + height // 2 < -height * 0.25 and not down_chunk:
            sprite_groups = update_chunks(DOWN, (0.5, 1), sprite_groups, world, chunks)
            down_chunk = True

        if camera_x + width // 2 < -width // 2 and camera_y + height // 2 > -height // 2 and not right_up_chunk[0]:
            sprite_groups = update_chunks(RIGHT_UP, (0, 0.5), sprite_groups, world, chunks)
            right_up_chunk[0] = True
        if camera_x + width // 2 < -width // 2 and camera_y + height // 2 < -height // 2 and not right_down_chunk[0]:
            sprite_groups = update_chunks(RIGHT_DOWN, (0, 0.5), sprite_groups, world, chunks)
            right_down_chunk[0] = True
        if camera_x + width // 2 > -width // 2 and camera_y + height // 2 > -height // 2 and not left_up_chunk[0]:
            sprite_groups = update_chunks(LEFT_UP, (0.5, 1), sprite_groups, world, chunks)
            left_up_chunk[0] = True
            print(LEFT_UP, 0)
        if camera_x + width // 2 > -width // 2 and camera_y + height // 2 < -height // 2 and not left_down_chunk[0]:
            sprite_groups = update_chunks(LEFT_DOWN, (0.5, 1), sprite_groups, world, chunks)
            left_down_chunk[0] = True
            print(LEFT_DOWN, 0)

        if (camera_x + width // 2 < -width * 0.75 and camera_y + height // 2 > -height // 2 or
            camera_x + width // 2 < -width // 2 and camera_y + height // 2 > -height * 0.25) and \
                not right_up_chunk[1]:
            sprite_groups = update_chunks(RIGHT_UP, (0.5, 1), sprite_groups, world, chunks)
            right_up_chunk[1] = True
        if (camera_x + width // 2 < -width * 0.75 and camera_y + height // 2 < -height // 2 or
            camera_x + width // 2 < -width // 2 and camera_y + height // 2 < -height * 0.75) and \
                not right_down_chunk[1]:
            sprite_groups = update_chunks(RIGHT_DOWN, (0.5, 1), sprite_groups, world, chunks)
            right_down_chunk[1] = True
        if (camera_x + width // 2 > -width * 0.25 and camera_y + height // 2 > -height // 2 or
            camera_x + width // 2 > -width // 2 and camera_y + height // 2 > -height * 0.25) and \
                not left_up_chunk[1]:
            sprite_groups = update_chunks(LEFT_UP, (0, 0.5), sprite_groups, world, chunks)
            left_up_chunk[1] = True
            print(LEFT_UP, 1)
        if (camera_x + width // 2 > -width * 0.25 and camera_y + height // 2 < -height // 2 or
            camera_x + width // 2 > -width // 2 and camera_y + height // 2 < -height * 0.75) and \
                not left_down_chunk[1]:
            sprite_groups = update_chunks(LEFT_DOWN, (0, 0.5), sprite_groups, world, chunks)
            left_down_chunk[1] = True
            print(LEFT_DOWN, 1)

        # изменение положения всех чанков на дисплее
        for index_x in range(3):
            for index_y in range(3):
                screen.blit(chunks[index_x + 3 * index_y], (camera_x + width * index_x, camera_y + height * index_y))
        screen.blit(hero.image, (width // 2, height // 2))
        interface_group.draw(screen)
        item_group.draw(screen)
        for item in item_group:
            item.draw_amount(screen, item.pos_x, item.pos_y)
        pygame.display.flip()
        clock.tick(FPS)
