from pynoise.noisemodule import Billow, Clamp, Perlin, Exponent
from pynoise.noiseutil import noise_map_plane_gpu
from pynoise.noiseutil import RenderImage
from pynoise.noiseutil import GradientColor
from pynoise.colors import Color
import numpy

import objects

TILE_WIDTH = TILE_HEIGHT = 96
RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"


class World:
    def __init__(self, width, height, seed, screen_width, screen_height, sprite_groups=None):
        self.sprite_groups = sprite_groups
        self.width = width
        self.height = height
        self.seed = seed  # от -119599999999999999 до 179499999845941242 но это не точно
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.chunk_size_x = self.screen_width // TILE_WIDTH
        self.chunk_size_y = self.screen_height // TILE_HEIGHT

        self.hero_x = None
        self.hero_y = None
        self.tile_lines = None
        self.tile_grids = []
        self.object_lines = None
        self.object_grids = []

        self.main_chunk_x = None
        self.main_chunk_y = None

    # библиотека pynoise создаёт карту шума в виде одномерного массива, а этот метод превращает его в
    # двухмерный массив для удобного вычисления координат тайлов и объектов
    def create_matrix(self, line, matrix, spawn=False):
        # количество тайлов на экран
        spawn_x = None
        spawn_y = None
        # максимальное количество тайлов травы на координате y
        max_forest = 0

        for y in range(self.height):
            line_x = line[y * self.width:(y + 1) * self.width]
            if spawn:
                # количство тайлов травы на y координате
                number_of_forest = 0
                for tile_num in line_x:
                    if tile_num == 0:
                        number_of_forest += 1
                # если количество тайлов травы больше максимального количества
                if number_of_forest > max_forest:
                    max_forest = number_of_forest
                    for x in range(self.width):
                        # если рядом с тайлом песка есть тайл травы, то тайл с песком становиться местом спавна
                        if -0.2 <= line_x[x] < 0 and (line_x[x - 1] == 0 or line_x[x - 1] == 0):
                            # координаты центрального чанка, где единичный отрезок - это размеры чанка
                            self.main_chunk_x = x // self.chunk_size_x
                            self.main_chunk_y = (self.height - y) // self.chunk_size_y
                            # координаты спавна персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ
                            spawn_x = x % self.chunk_size_x * TILE_WIDTH
                            spawn_y = (self.height - y) % self.chunk_size_y * TILE_HEIGHT
                            break
            matrix.append(line_x)
        # разворот по координате y, так как pynoise создаёт массив задом на перёд
        matrix = matrix[::-1]
        if spawn:
            return matrix, spawn_x, spawn_y
        return matrix

    def create_world(self):
        # тип шума и его настройки
        source = Clamp(Billow(seed=self.seed), -1, 0)
        # карта шума в виде одномерного массива
        self.tile_lines = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=2,
                                              upper_x=6, lower_z=1, upper_z=5, source=source)
        self.tile_grids, self.hero_x, self.hero_y = self.create_matrix(self.tile_lines, self.tile_grids, spawn=True)
        return self.hero_x, self.hero_y

    def filling_the_world(self):
        # тип шума и его настройки
        source = Exponent(Perlin(frequency=100, seed=self.seed), 1.25)
        # карта шума в виде одномерного массива
        self.object_lines = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=6,
                                                upper_x=18, lower_z=1, upper_z=5, source=source)
        self.object_grids = self.create_matrix(self.object_lines, self.object_grids)

    def download_save(self, save_number):
        tile_girds_save = open(f"../saves/{save_number}/tile_positions", "r", encoding="utf8")
        tile_positions = tile_girds_save.readlines()
        tile_girds_save.close()
        self.tile_grids = list(map(lambda y: list(map(numpy.float64, y[:-1].split())), tile_positions))

        objects_gird_save = open(f"../saves/{save_number}/object_positions", "r", encoding="utf8")
        object_positions = objects_gird_save.readlines()
        objects_gird_save.close()
        self.object_grids = list(map(lambda y: list(map(numpy.float64, y[:-1].split())), object_positions))

        hero_position = open(f"../saves/{save_number}/hero_position", "r", encoding="utf8")
        self.hero_x, self.hero_y, self.main_chunk_x, self.main_chunk_y = list(map(int, hero_position.read().split()))
        hero_position.close()

    def draw(self, direction=None):
        tile_type = None
        # координаты левого верхнего чанка, где единичный отрезок - это размеры чанка
        start_x = self.main_chunk_x - 1
        start_y = self.main_chunk_y - 1

        # координаты правого нижнего чанка, где единичный отрезок - это размеры чанка
        final_x = start_x + 3
        final_y = start_y + 3

        start_index_x = -1
        index_y = -1
        # настройка для отрисовка лишь 3 чанков по направлении движения камеры
        if direction == RIGHT:
            start_x = final_x
            start_x -= 1
            start_index_x = 1
        if direction == LEFT:
            final_x = start_x
            final_x += 1
        if direction == UP:
            final_y = start_y
            final_y += 1
        if direction == DOWN:
            start_y = final_y
            start_y -= 1
            index_y = 1

        # присвоение каждому тайлу и объекту своего спрайта
        for chunk_y in range(start_y, final_y):
            index_y += 1
            index_x = start_index_x
            for chunk_x in range(start_x, final_x):
                index_x += 1
                for y in range(self.chunk_size_y):
                    for x in range(self.chunk_size_x):
                        # значение тайла
                        tile_num = self.tile_grids[chunk_y * self.chunk_size_y + y][chunk_x * self.chunk_size_x + x]
                        # значение объекта
                        object_num = self.object_grids[chunk_y * self.chunk_size_y + y][chunk_x * self.chunk_size_x + x]
                        tile_groups = [self.sprite_groups.chunk_groups[index_x + index_y * 3]]
                        object_groups = [self.sprite_groups.object_groups[index_x + index_y * 3]]

                        if -1 <= tile_num < -0.2:
                            tile_type = "water.png"
                            tile_groups.append(self.sprite_groups.water_tile_groups[index_x + index_y * 3])
                        if -0.2 <= tile_num < 0:
                            tile_type = "sand.png"
                            if 0.5 <= object_num:
                                object_groups.append(
                                    self.sprite_groups.for_extraction_with_pickaxe_groups[index_x + index_y * 3])
                                objects.Stone(object_groups, x, y,
                                              chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)
                        if tile_num == 0:
                            tile_type = "grass.png"
                            if 0.2 <= object_num < 0.5:
                                object_groups.append(
                                    self.sprite_groups.for_extraction_with_axe_groups[index_x + index_y * 3])
                                objects.Tree(object_groups, x, y,
                                             chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)
                            if 0.5 <= object_num:
                                object_groups.append(
                                    self.sprite_groups.for_extraction_with_pickaxe_groups[index_x + index_y * 3])
                                objects.Stone(object_groups, x, y,
                                              chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)
                        objects.Tile(tile_groups, tile_type, x, y,
                                     chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)

    def make_map(self):
        # определение цветов для мини карты в плитре RGB
        gradient = GradientColor()
        gradient.add_gradient_point(-1, Color(0, 0, 0.5))
        gradient.add_gradient_point(-0.2, Color(0.75, 0.75, 0.5))
        gradient.add_gradient_point(0, Color(0, 0.75, 0))
        gradient.add_gradient_point(1, Color(0.5, 0.75, 1))
        render = RenderImage()
        render.render(self.width, self.height, self.tile_lines, 'map.png', gradient)

    # метод для применения настроек для отрисовки 3 экранов и обновления координат для центрального чанка
    # по направлению движения
    def update(self, sprite_groups, direction):
        self.sprite_groups = sprite_groups
        if direction == RIGHT:
            self.main_chunk_x += 1
        if direction == LEFT:
            self.main_chunk_x -= 1
        if direction == UP:
            self.main_chunk_y -= 1
        if direction == DOWN:
            self.main_chunk_y += 1
        self.draw(direction)
