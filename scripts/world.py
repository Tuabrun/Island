from pynoise.noisemodule import Billow, Clamp, Perlin, Exponent
from pynoise.noiseutil import noise_map_plane_gpu
from pynoise.noiseutil import RenderImage
from pynoise.noiseutil import GradientColor
from pynoise.colors import Color

import objects

TILE_WIDTH = TILE_HEIGHT = 96


class World:
    def __init__(self, sprite_groups, width, height, seed, screen_width, screen_height):
        self.sprite_groups = sprite_groups
        self.width = width
        self.height = height
        self.seed = seed  # от -119599999999999999 до 179499999845941242 но это не точно
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.world_line = None
        self.world_grid = []
        self.objects_line = None
        self.objects_grid = []

        self.main_chunk_x = None
        self.main_chunk_y = None

    # библиотека pynoise создаёт карту шума в виде одномерного массива, а этот метод превращает его в
    # двухмерный массив для удобного вычисления координат тайлов и объектов
    def create_matrix(self, line, matrix, spawn=False):
        # количество тайлов на экран
        chunk_size_x = self.screen_width // TILE_WIDTH
        chunk_size_y = self.screen_height // tile_height
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
                            # координаты центрального чанка, где еденичный отрезок - это размеры чанка
                            self.main_chunk_x = x // chunk_size_x
                            self.main_chunk_y = (self.height - y) // chunk_size_y
                            # координаты спавна персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ
                            spawn_x = x % chunk_size_x * TILE_WIDTH
                            spawn_y = (self.height - y) % chunk_size_y * tile_height
                            break
            matrix.append(line_x)
        # разворот по координате y, так как pynoise создаёт массив задом на перёд
        matrix = matrix[::-1]
        if spawn:
            return matrix, spawn_x, spawn_y
        return matrix

    def create_world(self):
        # тип шума и его настройки
        sourse = Clamp(Billow(seed=self.seed), -1, 0)
        # карта шума в виде одномерного массива
        self.world_line = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=2,
                                              upper_x=6, lower_z=1, upper_z=5, source=sourse)
        self.world_grid, spawn_x, spawn_y = self.create_matrix(self.world_line, self.world_grid, spawn=True)
        return spawn_x, spawn_y

    def filling_the_world(self):
        # тип шума и его настройки
        sourse = Exponent(Perlin(frequency=100, seed=self.seed), 1.25)
        # карта шума в виде одномерного массива
        self.objects_line = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=6,
                                                upper_x=18, lower_z=1, upper_z=5, source=sourse)
        self.objects_grid = self.create_matrix(self.objects_line, self.objects_grid)

    def draw(self, direction=None):
        tile_type = None
        chunk_size_x = int(self.screen_width // TILE_WIDTH)
        chunk_size_y = int(self.screen_height // tile_height)
        # координаты левого верхнего чанка, где еденичный отрезок - это размеры чанка
        start_x = self.main_chunk_x - 1
        start_y = self.main_chunk_y - 1

        # координаты правого нижнего чанка, где еденичный отрезок - это размеры чанка
        final_x = start_x + 3
        final_y = start_y + 3

        start_index_x = -1
        index_y = -1
        # настройка для отрисовка лишь 3 чанков по направлении движения камеры
        if direction == "up":
            final_y = start_y
            final_y += 1
        if direction == "down":
            start_y = final_y
            start_y -= 1
            index_y = 1
        if direction == "right":
            start_x = final_x
            start_x -= 1
            start_index_x = 1
        if direction == "left":
            final_x = start_x
            final_x += 1

        # присвоение каждому тайлу и объекту своего спрайта
        for chunk_y in range(start_y, final_y):
            index_y += 1
            index_x = start_index_x
            for chunk_x in range(start_x, final_x):
                index_x += 1
                for y in range(chunk_size_y):
                    for x in range(chunk_size_x):
                        # значение тайла
                        tile_num = self.world_grid[chunk_y * chunk_size_y + y][chunk_x * chunk_size_x + x]
                        # значение объекта
                        object_num = self.objects_grid[chunk_y * chunk_size_y + y][chunk_x * chunk_size_x + x]
                        if -1 <= tile_num < -0.2:
                            tile_type = "water.png"
                        if -0.2 <= tile_num < 0:
                            tile_type = "sand0.png"
                            if 0.5 <= object_num:
                                objects.Stone(self.sprite_groups.get_group_of_objects()[index_x + index_y * 3], x, y)
                        if tile_num == 0:
                            tile_type = "grass.png"
                            if 0.2 <= object_num < 0.5:
                                objects.Tree(self.sprite_groups.get_group_of_objects()[index_x + index_y * 3], x, y)
                            if 0.5 <= object_num:
                                objects.Stone(self.sprite_groups.get_group_of_objects()[index_x + index_y * 3], x, y)
                        if tile_num == 1:
                            tile_type = "pers.png"
                        objects.Tile(self.sprite_groups.get_group_of_chunks()[index_x + index_y * 3], tile_type, x, y)

    def make_map(self):
        # определение цветов для мини карты в плитре RGB
        gradient = GradientColor()
        gradient.add_gradient_point(-1, Color(0, 0, 0.5))
        gradient.add_gradient_point(-0.2, Color(0.75, 0.75, 0.5))
        gradient.add_gradient_point(0, Color(0, 0.75, 0))
        gradient.add_gradient_point(1, Color(0.5, 0.75, 1))
        render = RenderImage()
        render.render(self.width, self.height, self.world_line, 'map.png', gradient)

    # метод для применения настроек для отрисовки 3 экранов и обновления координат для центрального чанка
    # по направлению движения
    def update(self, sprite_groups, direction):
        self.sprite_groups = sprite_groups
        if direction == "up":
            self.main_chunk_y -= 1
        if direction == "down":
            self.main_chunk_y += 1
        if direction == "right":
            self.main_chunk_x += 1
        if direction == "left":
            self.main_chunk_x -= 1
        self.draw(direction)
