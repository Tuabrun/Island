import pygame
from pygame.locals import *

"""from numba import njit, prange"""

from button import Button
from world import World
from save_game import save_game
import creatures
from inventory import HotBar
from inventory import PopUpWindow
from file_directory import file_directory
from print_text import print_text

from constants import SPEED, HERO_SIZE, RIGHT, LEFT, UP, DOWN, RIGHT_UP, RIGHT_DOWN, LEFT_UP, LEFT_DOWN


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


def motion(direction, camera, hero_pos, speed):
    if direction in [RIGHT, DOWN]:
        camera -= speed
        hero_pos += speed
    if direction in [LEFT, UP]:
        camera += speed
        hero_pos -= speed
    return camera, hero_pos


def update_chunks(direction, sprite_groups_chunks):
    offset = None
    saved_chunks = None
    if direction == RIGHT:
        offset = 1
        saved_chunks = [0, 1, 3, 4, 6, 7]
    if direction == LEFT:
        offset = -1
        saved_chunks = [1, 2, 4, 5, 7, 8]
    if direction == UP:
        offset = -3
        saved_chunks = list(range(3, 9))
    if direction == DOWN:
        offset = 3
        saved_chunks = list(range(6))
    sprite_groups_chunks_copy = SpriteGroupsForChunks()
    for index in saved_chunks:
        for group_of_sprites in range(len(sprite_groups_chunks.get_all_sprite_groups())):
            sprite_groups_chunks_copy.get_all_sprite_groups()[group_of_sprites][index] = \
                sprite_groups_chunks.get_all_sprite_groups()[group_of_sprites][index + offset]
    sprite_groups_chunks = sprite_groups_chunks_copy
    return sprite_groups_chunks


def find_nearest_sprite(hero, sprite_groups_chunks, hero_x, hero_y, width, height):
    sprite_inf = hero.find_nearest_sprite(sprite_groups_chunks, hero_x, hero_y, width, height)
    if sprite_inf[0] is not None:
        return sprite_inf
    return None


def menu_cycle(screen, sprites, click_sound):
    menu_background = sprites["background"]
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


"""@njit(fastmath=True, parallel=True)"""
def game_cycle(screen, width, height, save_number, sprites, step_sound):
    sprite_groups_chunks = SpriteGroupsForChunks()
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

    world = World(900, 450, 2, width, height, sprites, sprite_groups_chunks)
    # координаты персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ
    # пояснение: в игре отрисовываются лишь 9 чанков, и в центральном чанке находится персонаж
    # как раз таки поэтому каждая группа спрайтов повторялатсь 9 раз. Каждой группе спрайтов соответствует свой чанк
    world.load_save(save_number)
    hero_x, hero_y = world.hero_x, world.hero_y
    # присваивание тайлам и объектам соответствующие спрайты
    world.draw()

    # создание чанков
    chunks = []
    for _ in range(9):
        chunk = pygame.Surface((width, height)).convert()
        chunk.set_alpha(None)
        chunks.append(chunk)
    # отрисовка спрайтов на этих чанках
    sprite_groups_chunks.draw(chunks)

    # флаги, показывающие подгружен нужный чанк или нет
    right_chunk = left_chunk = up_chunk = down_chunk = True
    right_up_chunk = [True, True]
    right_down_chunk = [True, True]
    left_up_chunk = [True, True]
    left_down_chunk = [True, True]
    last_direction = None

    hot_bar = HotBar(interface_group, sprites, true_width, true_height)

    hero = creatures.Hero(hero_group, sprites, 0, HERO_SIZE, HERO_SIZE)
    sprite = target_x = target_y = None
    speed = 3

    # координаты центрального чанка на дисплее
    camera_x, camera_y = -hero_x - width // 2, -hero_y - height // 2
    # переменные, отвечающие за движение камеры
    motion_x = motion_y = None

    running = True
    stones = 0
    XXX = 0
    while running:
        time = clock.tick()
        XXX += time
        if XXX >= 100:
            XXX = 0
        if time != 0:
            speed = time / SPEED
            hero.speed = speed

        if target_x is not None and -HERO_SIZE + speed + 1 < target_x < HERO_SIZE - speed - 1:
            motion_x = None
        if target_y is not None and -HERO_SIZE + speed + 1 < target_y < HERO_SIZE - speed - 1:
            motion_y = None

        for event in pygame.event.get():
            # нажатие крестика в правом верхнем углу
            if event.type == pygame.QUIT:
                save_game(save_number, world, hero_x, hero_y)
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(save_number, world, hero_x, hero_y)
                    game_finish_cycle(screen, true_width, true_height, interface_group, stones)
                    return False

                if event.key == pygame.K_d:
                    motion_x = RIGHT
                if event.key == pygame.K_a:
                    motion_x = LEFT
                if event.key == pygame.K_w:
                    motion_y = UP
                if event.key == pygame.K_s:
                    motion_y = DOWN

                if event.key == pygame.K_1:
                    hero.what_is_in_hands = "axe"
                if event.key == pygame.K_2:
                    hero.what_is_in_hands = "pickaxe"

                if event.key == pygame.K_f:
                    sprite, target_x, target_y = find_nearest_sprite(hero, sprite_groups_chunks,
                                                                     hero_x, hero_y, width, height)

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

        stop_motion = hero.check_collision(sprite_groups_chunks.get_material_sprite_groups(), motion_x, motion_y,
                                           hero_x, hero_y, width, height)

        if target_x is not None and stop_motion[0] != RIGHT and target_x > HERO_SIZE - speed - 1:
            camera_x, hero_x = motion(RIGHT, camera_x, hero_x, speed)
            step_counter += speed / 3
            stop_motion[0] = RIGHT
            motion_x = RIGHT
            target_x -= speed
        if target_x is not None and stop_motion[0] != LEFT and target_x < -HERO_SIZE - speed - 1:
            camera_x, hero_x = motion(LEFT, camera_x, hero_x, speed)
            step_counter += speed / 3
            stop_motion[0] = LEFT
            motion_x = LEFT
            target_x += speed
        if target_y is not None and stop_motion[1] != UP and target_y < -HERO_SIZE - speed - 1:
            camera_y, hero_y = motion(UP, camera_y, hero_y, speed)
            step_counter += speed / 3
            stop_motion[1] = UP
            motion_y = UP
            target_y += speed
        if target_y is not None and stop_motion[1] != DOWN and target_y > HERO_SIZE - speed - 1:
            camera_y, hero_y = motion(DOWN, camera_y, hero_y, speed)
            step_counter += speed / 3
            stop_motion[1] = DOWN
            motion_y = DOWN
            target_y -= speed

        if motion_x == RIGHT and stop_motion[0] != RIGHT:
            camera_x, hero_x = motion(RIGHT, camera_x, hero_x, speed)
            step_counter += speed / 3
        if motion_x == LEFT and stop_motion[0] != LEFT:
            camera_x, hero_x = motion(LEFT, camera_x, hero_x, speed)
            step_counter += speed / 3
        if motion_y == UP and stop_motion[1] != UP:
            camera_y, hero_y = motion(UP, camera_y, hero_y, speed)
            step_counter += speed / 3
        if motion_y == DOWN and stop_motion[1] != DOWN:
            camera_y, hero_y = motion(DOWN, camera_y, hero_y, speed)
            step_counter += speed / 3

        if hero_x >= width:
            if not up_chunk:
                world.update(sprite_groups_chunks, UP, (0, 0.5))
            if not down_chunk:
                world.update(sprite_groups_chunks, DOWN, (0.5, 1))
            if not right_up_chunk[0]:
                world.update(sprite_groups_chunks, RIGHT_UP, (0.5, 1))
            if not right_up_chunk[1]:
                world.update(sprite_groups_chunks, RIGHT_UP, (0, 0.5))
            if not right_down_chunk[0]:
                world.update(sprite_groups_chunks, RIGHT_DOWN, (0, 0.5))
            if not right_down_chunk[1]:
                world.update(sprite_groups_chunks, RIGHT_DOWN, (0.5, 1))
            camera_x += width
            hero_x -= width
            sprite_groups_chunks = update_chunks(RIGHT, sprite_groups_chunks)
            world.update(sprite_groups_chunks, RIGHT, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            last_direction = RIGHT
            right_chunk = False
            right_up_chunk = [False, False]
            right_down_chunk = [False, False]
            left_chunk = up_chunk = down_chunk = True
            left_up_chunk = [True, True]
            left_down_chunk = [True, True]
        if hero_x < 0:
            if not up_chunk:
                world.update(sprite_groups_chunks, UP, (0, 0.5))
            if not down_chunk:
                world.update(sprite_groups_chunks, DOWN, (0.5, 1))
            if not left_up_chunk[0]:
                world.update(sprite_groups_chunks, LEFT_UP, (0.5, 1))
            if not left_up_chunk[1]:
                world.update(sprite_groups_chunks, LEFT_UP, (0, 0.5))
            if not left_down_chunk[0]:
                world.update(sprite_groups_chunks, LEFT_DOWN, (0, 0.5))
            if not left_down_chunk[1]:
                world.update(sprite_groups_chunks, LEFT_DOWN, (0.5, 1))
            camera_x -= width
            hero_x += width
            sprite_groups_chunks = update_chunks(LEFT, sprite_groups_chunks)
            world.update(sprite_groups_chunks, LEFT, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            last_direction = LEFT
            left_chunk = False
            left_up_chunk = [False, False]
            left_down_chunk = [False, False]
            right_chunk = up_chunk = down_chunk = True
            right_up_chunk = [True, True]
            right_down_chunk = [True, True]
        if hero_y < 0:
            if not right_chunk:
                world.update(sprite_groups_chunks, RIGHT, (0.5, 1))
            if not left_chunk:
                world.update(sprite_groups_chunks, LEFT, (0, 0.5))
            if not right_up_chunk[0]:
                world.update(sprite_groups_chunks, RIGHT_UP, (0.5, 1))
            if not right_up_chunk[1]:
                world.update(sprite_groups_chunks, RIGHT_UP, (0, 0.5))
            if not left_up_chunk[0]:
                world.update(sprite_groups_chunks, LEFT_UP, (0.5, 1))
            if not left_up_chunk[1]:
                world.update(sprite_groups_chunks, LEFT_UP, (0, 0.5))
            camera_y -= height
            hero_y += height
            sprite_groups_chunks = update_chunks(UP, sprite_groups_chunks)
            world.update(sprite_groups_chunks, UP, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            last_direction = UP
            up_chunk = False
            right_up_chunk = [False, False]
            left_up_chunk = [False, False]
            right_chunk = left_chunk = down_chunk = True
            right_down_chunk = [True, True]
            left_down_chunk = [True, True]
        if hero_y >= height:
            if not right_chunk:
                world.update(sprite_groups_chunks, RIGHT, (0.5, 1))
            if not left_chunk:
                world.update(sprite_groups_chunks, LEFT, (0, 0.5))
            if not right_down_chunk[0]:
                world.update(sprite_groups_chunks, RIGHT_DOWN, (0, 0.5))
            if not right_down_chunk[1]:
                world.update(sprite_groups_chunks, RIGHT_DOWN, (0.5, 1))
            if not left_down_chunk[0]:
                world.update(sprite_groups_chunks, LEFT_DOWN, (0, 0.5))
            if not left_down_chunk[1]:
                world.update(sprite_groups_chunks, LEFT_DOWN, (0.5, 1))
            camera_y += height
            hero_y -= height
            sprite_groups_chunks = update_chunks(DOWN, sprite_groups_chunks)
            world.update(sprite_groups_chunks, DOWN, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            last_direction = DOWN
            down_chunk = False
            right_down_chunk = [False, False]
            left_down_chunk = [False, False]
            right_chunk = left_chunk = up_chunk = True
            right_up_chunk = [True, True]
            left_up_chunk = [True, True]

        if hero_x > width * 0.25 and not right_chunk:
            world.update(sprite_groups_chunks, RIGHT, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            right_chunk = True
        if hero_x < width * 0.75 and not left_chunk:
            world.update(sprite_groups_chunks, LEFT, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            left_chunk = True
        if hero_y < height * 0.75 and not up_chunk:
            world.update(sprite_groups_chunks, UP, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            up_chunk = True
        if hero_y > height * 0.25 and not down_chunk:
            world.update(sprite_groups_chunks, DOWN, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            down_chunk = True

        if hero_x > width // 2 and hero_y < height // 2 and not right_up_chunk[0]:
            world.update(sprite_groups_chunks, RIGHT_UP, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            right_up_chunk[0] = True
        if hero_x > width // 2 and hero_y > height // 2 and not right_down_chunk[0]:
            world.update(sprite_groups_chunks, RIGHT_DOWN, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            right_down_chunk[0] = True
        if hero_x < width // 2 and hero_y < height // 2 and not left_up_chunk[0]:
            world.update(sprite_groups_chunks, LEFT_UP, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            left_up_chunk[0] = True
        if hero_x < width // 2 and hero_y > height // 2 and not left_down_chunk[0]:
            world.update(sprite_groups_chunks, LEFT_DOWN, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            left_down_chunk[0] = True

        if ((hero_x > width * 0.75 and hero_y < height // 2 and last_direction == RIGHT) or
            (hero_x > width // 2 and hero_y < height * 0.25 and last_direction == UP))\
                and not right_up_chunk[1]:
            world.update(sprite_groups_chunks, RIGHT_UP, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            right_up_chunk[1] = True
        if ((hero_x > width * 0.75 and hero_y > height // 2 and last_direction == RIGHT) or
            (hero_x > width // 2 and hero_y > height * 0.75 and last_direction == DOWN))\
                and not right_down_chunk[1]:
            world.update(sprite_groups_chunks, RIGHT_DOWN, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            right_down_chunk[1] = True
        if ((hero_x < width * 0.25 and hero_y < height // 2 and last_direction == LEFT) or
            (hero_x < width // 2 and hero_y < height * 0.25 and last_direction == UP))\
                and not left_up_chunk[1]:
            world.update(sprite_groups_chunks, LEFT_UP, (0, 0.5))
            sprite_groups_chunks.draw(chunks)
            left_up_chunk[1] = True
        if ((hero_x < width * 0.25 and hero_y > height // 2 and last_direction == LEFT) or
            (hero_x < width // 2 and hero_y > height * 0.75 and last_direction == DOWN))\
                and not left_down_chunk[1]:
            world.update(sprite_groups_chunks, LEFT_DOWN, (0.5, 1))
            sprite_groups_chunks.draw(chunks)
            left_down_chunk[1] = True

        # изменение положения всех чанков на дисплее
        for index_x in range(3):
            for index_y in range(3):
                screen.blit(chunks[index_x + 3 * index_y], (camera_x + width * index_x, camera_y + height * index_y))
        screen.blit(hero.image, (width // 2, height // 2))

        interface_group.draw(screen)  # поправить
        item_group.draw(screen)  # поправить
        for item in item_group:
            item.draw_amount(screen, item.pos_x, item.pos_y)  # поправить
        if XXX == 0:
            fps = round(1000 / time, 1)
        print_text(screen, 20, 20, f"FPS: {fps}", font_color=(255, 0, 0), font_size=30)
        pygame.display.flip()
