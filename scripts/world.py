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
RIGHT_UP = "right_up"
RIGHT_DOWN = "right_down"
LEFT_UP = "left_up"
LEFT_DOWN = "left_down"


# класс для создания мира, наполнения его объктами, присвоения значениям соответствующих спрайтов, загрузки сохранеия
# и обновления экрана
class World:
    def __init__(self, width, height, seed, screen_width, screen_height, sprites=None, sprite_groups=None):
        # класс, хранящий все группы спрайтов для чанков. Подробнее о нём можно прочитать в классе
        # SpriteGroupsForChunks в cycles.py
        self.sprite_groups = sprite_groups

        # размеры карты по x и по y, где единичный отрезок - это размеры чанка или 1 пиксель для мини-карты
        self.width = width
        self.height = height

        # сид для создания карты. Он необходим для получения разных карт
        self.seed = seed  # от -119599999999999999 до 179499999845941242 но это не точно. Потом надо будет протестить

        # числа, максимально приближненные к размеру экрана по x и по y делящееся нацело на размер тайла
        self.screen_width = screen_width
        self.screen_height = screen_height

        # числа, равные максимальному колличеству тайлов на экране по x и по y
        self.chunk_size_x = self.screen_width // TILE_WIDTH
        self.chunk_size_y = self.screen_height // TILE_HEIGHT

        # словарь спрайтов, необходимый для иницилизации объектов
        self.sprites = sprites

        # координаты персонажа внутри чанка
        self.hero_x = None
        self.hero_y = None

        # одномерные массивы значений, соответствующих тайлам и объектам. Необходимы только для создания мини-карт
        # и и соответствующих им двумерным массивам.
        # (массивы идут задом на перёд по y. То-есть если представить, что это двумерные массивы, то сначала будут
        # идти последние строки)
        self.tile_lines = None
        self.object_lines = None

        # двумерные массивы значений, соответствующих тайлам и объектам. Необходимы для всей остальной работы с миром.
        # (идут в нормальном порядке)
        self.tile_grids = []
        self.object_grids = []

        # координаты чанка, в котором находится персонаж
        self.main_chunk_x = None
        self.main_chunk_y = None
        self.build = False

    # библиотека pynoise создаёт карту шума в виде одномерного массива, а этот метод превращает его в
    # двухмерный массив и разворачивает его задом на перёд для удобного вычисления координат тайлов и объектов
    def create_matrix(self, line, spawn=False):
        # line - одномерный массив, который необходимо превратить в двумерный
        # spawn - нужно ли создавать координаты спавна для персонажа

        # возвращаемый двумерный массив
        matrix = []

        # координы спавна персонажа
        spawn_x = None
        spawn_y = None

        # максимальное количество тайлов травы в стоке
        max_forest = 0

        # цикл, проходящий по каждой строчке будующкго двумерного массива. Он делит одномерный массив
        # на строчки, навные равные размеру карты по x
        for y in range(self.height):
            # строчка начинается с числа, кратного размеру карты по x, или с 0, а заканчивается началом следующей
            # строчки, потому, что python не включает послееднее число. То-есть если взять line[0:256], где 256 - это
            # размер карты по x, то будут взяты значения от 0 до 255
            line_x = line[y * self.width:(y + 1) * self.width]

            # если необходимо задать координаты спавна для персонажа
            if spawn:
                # количство тайлов травы в строке. То-есть цикл проходится по каждому значению строки, и если строка
                # равна 0, то к счётчику прибавляется 1, так как значению 0 соответствует тайл травы
                number_of_forest = 0
                for tile_num in line_x:
                    if tile_num == 0:
                        number_of_forest += 1

                # если количество тайлов травы больше максимального количества. Потому, что персонаж должен заспавниться
                # на достаточно большом острове для нормального развития
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

        # карта шума в виде двумерного массива и координаты спавна персонажа
        self.tile_grids, self.hero_x, self.hero_y = self.create_matrix(self.tile_lines, spawn=True)
        return self.hero_x, self.hero_y

    def filling_the_world(self):
        # тип шума и его настройки
        source = Exponent(Perlin(frequency=100, seed=self.seed), 1.25)

        # карта шума в виде одномерного массива
        self.object_lines = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=6,
                                                upper_x=18, lower_z=1, upper_z=5, source=source)

        # карта шума в виде двумерного массива
        self.object_grids = self.create_matrix(self.object_lines)
        self.object_grids[self.main_chunk_y * self.chunk_size_y
                          + self.hero_y // TILE_HEIGHT][self.main_chunk_x * self.chunk_size_x
                                                        + self.hero_x // TILE_WIDTH + 1] = 2

    def load_save(self, save_number):
        # save_number - номер папки сохранения

        # чтение файла с сохранением мира, то-есть со значениями для тайлов
        tile_girds_save = open(f"../saves/{save_number}/tile_positions", "r", encoding="utf8")
        # нарезка файла на строки, соответствующие строкам из двумерного массива для значений, соответствующих
        # тайлам, в этот массив
        tile_positions = tile_girds_save.readlines()
        # закрытие файла
        tile_girds_save.close()
        # конвертация значений из файла в тип данных numpy.float64 из стокового типа и их запись в этот массив
        self.tile_grids = list(map(lambda y: list(map(numpy.float64, y[:-1].split())), tile_positions))

        # чтение файла с сохранением объектов, то-есть со значениями для объектов
        objects_gird_save = open(f"../saves/{save_number}/object_positions", "r", encoding="utf8")
        # нарезка файла на строки, соответствующие строкам из двумерного массива для значений, соответствующих
        # объектам, в этот массив
        object_positions = objects_gird_save.readlines()
        # закрытие файла
        objects_gird_save.close()
        # конвертация значений из файла в тип данных numpy.float64 из стокового типа и их запись в этот массив
        self.object_grids = list(map(lambda y: list(map(numpy.float64, y[:-1].split())), object_positions))

        # чтение файла с сохранением координат персонажа внутри чанка и координат чанка, в котором находится персонаж
        hero_position = open(f"../saves/{save_number}/hero_position", "r", encoding="utf8")
        # присвоение этих значений соответствующим переменным
        self.hero_x, self.hero_y, self.main_chunk_x, self.main_chunk_y = list(map(int, hero_position.read().split()))
        # закрытие файла
        hero_position.close()

    def draw(self, direction=None, piece=(0, 1)):
        tile_type = None
        # координаты левого верхнего чанка, где единичный отрезок - это размеры чанка
        start_chunk_x = self.main_chunk_x - 1
        start_chunk_y = self.main_chunk_y - 1
        chunks_x = [start_chunk_x, start_chunk_x + 1, start_chunk_x + 2]
        chunks_y = [start_chunk_y, start_chunk_y + 1, start_chunk_y + 2]

        if direction in (RIGHT, LEFT):
            start_x = self.chunk_size_x * piece[0]
            start_y = 0
            final_x = self.chunk_size_x * piece[1]
            final_y = self.chunk_size_y
        else:
            start_x = 0
            start_y = self.chunk_size_y * piece[0]
            final_x = self.chunk_size_x
            final_y = self.chunk_size_y * piece[1]

        if direction == RIGHT:
            chunks_x = [start_chunk_x + 2]
            chunks_y = [start_chunk_y + 1]
        if direction == LEFT:
            chunks_x = [start_chunk_x]
            chunks_y = [start_chunk_y + 1]
        if direction == UP:
            chunks_x = [start_chunk_x + 1]
            chunks_y = [start_chunk_y]
        if direction == DOWN:
            chunks_x = [start_chunk_x + 1]
            chunks_y = [start_chunk_y + 2]

        if direction == RIGHT_UP:
            chunks_x = [start_chunk_x + 2]
            chunks_y = [start_chunk_y]
        if direction == RIGHT_DOWN:
            chunks_x = [start_chunk_x + 2]
            chunks_y = [start_chunk_y + 2]
        if direction == LEFT_UP:
            chunks_x = [start_chunk_x]
            chunks_y = [start_chunk_y]
        if direction == LEFT_DOWN:
            chunks_x = [start_chunk_x]
            chunks_y = [start_chunk_y + 2]

        # присвоение каждому тайлу и объекту своего спрайта
        # прохождение от начального до финального чанка по y
        for chunk_y in chunks_y:
            index_y = chunk_y - start_chunk_y
            # прохождение от начального до финального чанка по x
            for chunk_x in chunks_x:
                index_x = chunk_x - start_chunk_x
                # прохождение по каждому элементу чанка по y
                for y in range(int(start_y), int(final_y)):
                    # прохождение по каждому элементу чанка по x
                    for x in range(int(start_x), int(final_x)):
                        # значение тайла
                        tile_num = self.tile_grids[chunk_y * self.chunk_size_y + y][chunk_x * self.chunk_size_x + x]
                        # значение объекта
                        object_num = self.object_grids[chunk_y * self.chunk_size_y + y][chunk_x * self.chunk_size_x + x]

                        # группы спрайтов, в которые нужно добавить спрайт тайла
                        tile_groups = [self.sprite_groups.chunk_groups[index_x + index_y * 3]]
                        # группы спрайтов, в которые нужно добавить спрайт объекта
                        object_groups = [self.sprite_groups.object_groups[index_x + index_y * 3]]

                        # если значение находится в этом диапазоне, то оно соответствует тайлу воды
                        if -1 <= tile_num < -0.2:
                            tile_type = "water"
                            # добавление к группам спрайтов для этого тайла группу спрайтов для тайлов воды
                            tile_groups.append(self.sprite_groups.water_tile_groups[index_x + index_y * 3])

                        # если значение находится в этом диапазоне, то оно соответствует тайлу песка
                        if -0.2 <= tile_num < 0:
                            tile_type = "sand"
                            # валун может находиться на тайле песка, поэтому
                            # если на этом же месте в массиве с объектами находится значение большее или равное этому,
                            # то оно равно валуну
                            if 0.5 <= object_num < 2:
                                # добавление к группам спрайтов для этого валуна группу спрайтов, элементы которой
                                # можно сломать киркой
                                object_groups.append(
                                    self.sprite_groups.for_extraction_with_pickaxe_groups[index_x + index_y * 3])

                                # создания экземпляра класса валуна
                                objects.Boulder(object_groups, self.sprites, x, y,
                                                chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)

                        # если значение находится в этом диапазоне, то оно соответствует тайлу травы
                        if tile_num == 0:
                            tile_type = "grass"
                            # валун или дерево могут находиться на тайле травы, поэтому:

                            # если на этом же месте в массиве с объектами находится в этом диапазоне,
                            # то оно равно дереву
                            if 0.2 <= object_num < 0.5:
                                # добавление к группам спрайтов для этого дерева группу спрайтов, элементы которой
                                # можно сломать топором
                                object_groups.append(
                                    self.sprite_groups.for_extraction_with_axe_groups[index_x + index_y * 3])

                                # создания экземпляра класса дерева
                                objects.Tree(object_groups, self.sprites, x, y,
                                             chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)

                            # если на этом же месте в массиве с объектами находится значение большее или равное этому,
                            # то оно равно валуну
                            if 0.5 <= object_num:
                                # добавление к группам спрайтов для этого валуна группу спрайтов, элементы которой
                                # можно сломать киркой
                                object_groups.append(
                                    self.sprite_groups.for_extraction_with_pickaxe_groups[index_x + index_y * 3])

                                # создания экземпляра класса валуна
                                objects.Boulder(object_groups, self.sprites, x, y,
                                                chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)

                        # создания экземпляра класса тайла, которому соответствуют вычесленные выше значения
                        objects.Tile(tile_groups, self.sprites, tile_type, x, y,
                                     chunk_x * self.chunk_size_x, chunk_y * self.chunk_size_y)

    def make_map(self):
        # определение цветов для мини карты в плитре RGB
        gradient = GradientColor()
        gradient.add_gradient_point(-1, Color(0, 0, 0.5))
        gradient.add_gradient_point(-0.2, Color(0.75, 0.75, 0.5))
        gradient.add_gradient_point(0, Color(0, 0.75, 0))
        gradient.add_gradient_point(1, Color(0.5, 0.75, 1))
        render = RenderImage()
        # создание мини-карты
        render.render(self.width, self.height, self.tile_lines, 'map.png', gradient)

    # метод для применения настроек для отрисовки 3 экранов и обновления координат для центрального чанка
    # по направлению движения
    def update(self, sprite_groups, direction, piece):
        # обновление группы спрайтов
        self.sprite_groups = sprite_groups
        if direction == RIGHT and piece == (0, 0.5):
            self.main_chunk_x += 1
        if direction == LEFT and piece == (0.5, 1):
            self.main_chunk_x -= 1
        if direction == UP and piece == (0.5, 1):
            self.main_chunk_y -= 1
        if direction == DOWN and piece == (0, 0.5):
            self.main_chunk_y += 1
        self.draw(direction, piece)
