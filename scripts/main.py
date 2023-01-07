import pygame
from pygame.locals import *

from world import World
import creatures


# класс для хранения и отрисовки групп спрайтов
class SpritesGroupsForChunks:
    def __init__(self):
        self.group_of_chunks = []
        self.group_of_objects = []
        self.group_of_water_tiles = []
        # каждая группа спрайтов повторяется 9 раз и передаётся в соответствующий массив
        # далее я поясню зачем это нужно
        for _ in range(9):
            tiles_group = pygame.sprite.Group()
            water_tiles_group = pygame.sprite.Group()
            objects_group = pygame.sprite.Group()
            self.group_of_chunks.append(tiles_group)
            self.group_of_water_tiles.append(water_tiles_group)
            self.group_of_objects.append(objects_group)

    def get(self):
        return [self.group_of_chunks, self.group_of_objects]

    # метод для отрисовки групп спрайтов. Принимает на вход массив из surface
    # далее названием chunk будет называться surface размером с экран
    def draw(self, chunks):
        for sprite_group in self.get():
            for i in range(9):
                sprite_group[i].draw(chunks[i])


if __name__ == '__main__':
    TILE_WIDTH = TILE_HEIGHT = 96
    SPEED = 3

    pygame.init()
    infoObject = pygame.display.Info()
    # ширина экрана
    width = infoObject.current_w // TILE_WIDTH * TILE_WIDTH
    # высота экрана
    height = infoObject.current_h // TILE_HEIGHT * TILE_HEIGHT

    sprite_groups = SpritesGroupsForChunks()
    hero_group = pygame.sprite.Group()

    # создание окна
    flags = FULLSCREEN | DOUBLEBUF
    screen = pygame.display.set_mode((width, height), flags)
    screen.set_alpha(None)

    FPS = 60  # число кадров в секунду
    clock = pygame.time.Clock()

    # ограничение списка проверяемых событий для лучшей производительности
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    world = World(sprite_groups, 900, 450, 2, width, height)
    # координаты персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ и создание мира
    # пояснение: в игре отрисовываются лишь 9 чанков, и в центральном чанке находится персонаж
    # как раз таки поэтому каждая группа спрайтов повторялатсь 9 раз. Каждой группе спрайтов соответствует свой чанк
    hero_pos_x, hero_pos_y = world.create_world()
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

    hero = creatures.Hero(hero_group, width, height)

    # координаты центрального чанка на дисплее
    camera_x, camera_y = -hero_pos_x - width // 2, -hero_pos_y - height // 2
    # переменные, отвечающие за движение камеры
    motion_x = motion_y = None

    running = True
    while running:
        for event in pygame.event.get():
            # нажатие крестика в правом верхнем углу
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    motion_y = "up"
                if event.key == pygame.K_s:
                    motion_y = "down"
                if event.key == pygame.K_d:
                    motion_x = "right"
                if event.key == pygame.K_a:
                    motion_x = "left"
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_s]:
                    motion_y = None
                if event.key in [pygame.K_d, pygame.K_a]:
                    motion_x = None

        motion = hero.udate(sprite_groups.group_of_water_tiles[4], motion_x, motion_y,
                            hero_pos_x // TILE_WIDTH, hero_pos_y // TILE_HEIGHT)

        if motion_y == "up" and not motion[1]:
            camera_y += SPEED
            hero_pos_y -= SPEED
        if motion_y == "down" and not motion[1]:
            camera_y -= SPEED
            hero_pos_y += SPEED
        if motion_x == "right" and not motion[0]:
            camera_x -= SPEED
            hero_pos_x += SPEED
        if motion_x == "left" and not motion[0]:
            camera_x += SPEED
            hero_pos_x -= SPEED

        # дальше идут 4 похожих блока пока, поэтому поясю за все сразу
        # если центральный чанк полностью ущёл за границы экрана (тоесть координаты его верхнего левого угла
        # либо меньше размера экрана по x или по y, либо больше 0), то первые 3 чанка по направлению движения
        # камеры полностью обновляют свои группы спрайтов, а остальные 6 чанков меняют свои группы спрайтов
        # на группу спрайтов соседа по направлению движения камеры. Соответственно меняется и главный чанк по
        # направлению движения камеры. В конце все группы спрайтов отрисовываюся на своих чанках, а положение
        # камеры смещается к персонажу на главном чанке
        if camera_y + height // 2 > 0:
            sprite_groups_copy = SpritesGroupsForChunks()
            for index in range(3, 9):
                for group_of_sprites in range(len(sprite_groups.get())):
                    sprite_groups_copy.get()[group_of_sprites][index] = sprite_groups.get()[group_of_sprites][index - 3]
                sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index - 3]
            sprite_groups = sprite_groups_copy
            world.update(sprite_groups, "up")
            sprite_groups.draw(chunks)
            camera_y = -height - height // 2
            hero_pos_y = width

        if camera_y + height // 2 < -height:
            sprite_groups_copy = SpritesGroupsForChunks()
            for index in range(6):
                for group_of_sprites in range(len(sprite_groups.get())):
                    sprite_groups_copy.get()[group_of_sprites][index] = sprite_groups.get()[group_of_sprites][index + 3]
                sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index + 3]
            sprite_groups = sprite_groups_copy
            world.update(sprite_groups, "down")
            sprite_groups.draw(chunks)
            camera_y = 0 - height // 2
            hero_pos_y = 0

        if camera_x + width // 2 < -width:
            sprite_groups_copy = SpritesGroupsForChunks()
            for index in [0, 1, 3, 4, 6, 7]:
                for group_of_sprites in range(len(sprite_groups.get())):
                    sprite_groups_copy.get()[group_of_sprites][index] = sprite_groups.get()[group_of_sprites][index + 1]
                sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index + 1]
            sprite_groups = sprite_groups_copy
            world.update(sprite_groups, "right")
            sprite_groups.draw(chunks)
            camera_x = 0 - width // 2
            hero_pos_x = 0

        if camera_x + width // 2 > 0:
            sprite_groups_copy = SpritesGroupsForChunks()
            for index in [1, 2, 4, 5, 7, 8]:
                for group_of_sprites in range(len(sprite_groups.get())):
                    sprite_groups_copy.get()[group_of_sprites][index] = sprite_groups.get()[group_of_sprites][index - 1]
                sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index - 1]
            sprite_groups = sprite_groups_copy
            world.update(sprite_groups, "left")
            sprite_groups.draw(chunks)
            camera_x = -width - width // 2
            hero_pos_x = width

        # изменение положения всех чанков на дисплее
        for index_x in range(3):
            for index_y in range(3):
                screen.blit(chunks[index_x + 3 * index_y], (camera_x + width * index_x, camera_y + height * index_y))
        hero_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
