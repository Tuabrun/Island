import pygame
from pygame.locals import *

from load_image import load_image
from button import Button
from world import World
import creatures

FPS = 60
SPEED = 3
RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"


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


def show_menu(screen):
    menu_background = load_image('background.jpg')
    start_button = Button(330, 60)
    quit_button = Button(135, 60)
    save_button = Button(400, 60)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.blit(menu_background, (0, 0))
        running = start_button.draw(780, 340, 'START GAME', "change_cycle")
        quit_button.draw(870, 565, 'QUIT', "quit")
        save_button.draw(750, 450, 'UPLOAD A SAVE')

        if not running:
            return True

        pygame.display.update()


def update_chunks(direction, sprite_groups, camera, hero_pos, screen_size, world, chunks):
    offset = None
    saved_chunks = None
    if direction == RIGHT:
        offset = 1
        saved_chunks = [0, 1, 3, 4, 6, 7]
        camera = 0 - screen_size // 2
        hero_pos = 0
    if direction == LEFT:
        offset = -1
        saved_chunks = [1, 2, 4, 5, 7, 8]
        camera = -screen_size + 1 - screen_size // 2
        hero_pos = screen_size - 1
    if direction == UP:
        offset = -3
        saved_chunks = list(range(3, 9))
        camera = -screen_size + 1 - screen_size // 2
        hero_pos = screen_size - 1
    if direction == DOWN:
        offset = 3
        saved_chunks = list(range(6))
        camera = 0 - screen_size // 2
        hero_pos = 0
    sprite_groups_copy = SpriteGroupsForChunks()
    for index in saved_chunks:
        for group_of_sprites in range(len(sprite_groups.get_all_sprite_groups())):
            sprite_groups_copy.get_all_sprite_groups()[group_of_sprites][index] = \
                sprite_groups.get_all_sprite_groups()[group_of_sprites][index + offset]
    sprite_groups = sprite_groups_copy
    world.update(sprite_groups, direction)
    sprite_groups.draw(chunks)
    return sprite_groups, camera, hero_pos


def game_cycle(screen, width, height, step_sound):
    sprite_groups = SpriteGroupsForChunks()
    hero_group = pygame.sprite.Group()

    step_counter = 0
    vol = 0.1

    # ограничение списка проверяемых событий для лучшей производительности
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    clock = pygame.time.Clock()
    counter = -1

    world = World(sprite_groups, 900, 450, 2, width, height)
    # координаты персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ и создание мира
    # пояснение: в игре отрисовываются лишь 9 чанков, и в центральном чанке находится персонаж
    # как раз таки поэтому каждая группа спрайтов повторялатсь 9 раз. Каждой группе спрайтов соответствует свой чанк
    hero_x, hero_y = world.create_world()
    # создание объектов вроде камня
    world.filling_the_world()
    # присваивание тайлам и объектам соответствующие спрайты
    world.draw()
    # создание карты
    world.make_map()

    # создание чанков
    chunks = []
    for index in range(9):
        chunk = pygame.Surface((width, height)).convert()
        chunk.set_alpha(None)
        chunks.append(chunk)
    # отрисовка спрайтов на этих чанках
    sprite_groups.draw(chunks)

    hero = creatures.Hero(hero_group)
    direction = RIGHT
    direction_x = direction_y = None
    sprite = target_x = target_y = None

    # координаты центрального чанка на дисплее
    camera_x, camera_y = -hero_x - width // 2, -hero_y - height // 2
    # переменные, отвечающие за движение камеры
    motion_x = motion_y = None

    running = True

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
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_d:
                    motion_x = direction_x = RIGHT
                if event.key == pygame.K_a:
                    motion_x = direction_x = LEFT
                if event.key == pygame.K_w:
                    motion_y = direction_y = UP
                if event.key == pygame.K_s:
                    motion_y = direction_y = DOWN

                if event.key == pygame.K_f:
                    sprite_inf = hero.find_nearest_sprite(sprite_groups, hero_x, hero_y, width, height)
                    sprite, target_x, target_y = sprite_inf

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
            action = "mine"
            direction = direction_x
            if counter in [31, 63, 95]:
                sprite.update()
                sprite_groups.draw(chunks)
        if motion_y is None and motion_x is None:
            frame_number = 0
        hero.update(action, direction, frame_number)

        # дальше идут 4 похожих блока пока, поэтому поясю за все сразу
        # если центральный чанк полностью ущёл за границы экрана (тоесть координаты его верхнего левого угла
        # либо меньше размера экрана по x или по y, либо больше 0), то первые 3 чанка по направлению движения
        # камеры полностью обновляют свои группы спрайтов, а остальные 6 чанков меняют свои группы спрайтов
        # на группу спрайтов соседа по направлению движения камеры. Соответственно меняется и главный чанк по
        # направлению движения камеры. В конце все группы спрайтов отрисовываюся на своих чанках, а положение
        # камеры смещается к персонажу на главном чанке
        if camera_x + width // 2 <= -width:
            sprite_groups, camera_x, hero_x = update_chunks(RIGHT, sprite_groups, camera_x,
                                                            hero_x, width, world, chunks)
        if camera_x + width // 2 > 0:
            sprite_groups, camera_x, hero_x = update_chunks(LEFT, sprite_groups, camera_x,
                                                            hero_x, width, world, chunks)
        if camera_y + height // 2 >= 0:
            sprite_groups, camera_y, hero_y = update_chunks(UP, sprite_groups, camera_y,
                                                            hero_y, height, world, chunks)
        if camera_y + height // 2 <= -height:
            sprite_groups, camera_y, hero_y = update_chunks(DOWN, sprite_groups, camera_y,
                                                            hero_y, height, world, chunks)

        # изменение положения всех чанков на дисплее
        for index_x in range(3):
            for index_y in range(3):
                screen.blit(chunks[index_x + 3 * index_y], (camera_x + width * index_x, camera_y + height * index_y))
        screen.blit(hero.get_image(), (width // 2, height // 2))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
