import pygame

from file_directory import file_directory
from print_text import print_text
from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96
RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"


def check_collision_at_the_border(border, chunk_size, object, sprite_group):
    # border - у какой границы находится объект
    # chunk_size - на сколько изменить значение. Эта переменная должна соответствовать границе
    # object - объект для которго проверяется столкновение
    # sprite_group - группа спрайтов, с которой проверяется столкновение

    # сохранение начальных координат
    pos_x = object.pos_x
    pos_y = object.pos_y

    # если объект находится на этих границах, то в зависимости от границы к координате может прибавиться или убавиться
    # количество тайлов, корорые могут поместиться на экране. Например, если объект находится у левой границы, то для
    # того, чтобы проверить столкновение с существом, находящимся у правой границы левого чанка, нужно к координате x
    # прибавить количество тайлов, которое может поместиться на 1 экране. Получится, что по x координате объект будет
    # находиться за пределом любого чанка справа. То-есть если объект находится на 0 координате по x, то после этого
    # прибавления он будет находиться на 20 координате по x, потому что если мы возьмём экран 1920*1080, то в него
    # может поместиться 20*11 тайлов 96*96 пикселей. Поскольку отсчёт начинается с 0, то 20 тайл - это позиция после
    # последнего чанка, то-есть за пределом этого чанка. Благодаря этому объект становиться частью левого чанка, откуда
    # уже проверяется столкновение с существом. А не становится он концом своего чанка потому, что каждый из 9 чанков
    # имеет координаты от 0 до размеров экрана, а значит объект с координатами (0;0) находится одновременно в 9 чанках.
    # Бага не происходит потому, что группы спрайтов тоже разделены на 9 штук для того, чтобы мы могли проверять
    # столкновение только со спрайтами определённого чанка.
    if border == RIGHT:
        object.pos_x -= chunk_size
    if border == LEFT:
        object.pos_x += chunk_size
    if border == UP:
        object.pos_y += chunk_size
    if border == DOWN:
        object.pos_y -= chunk_size

    # изменение координат объекта со значениями описанными выше
    object.rect = object.image.get_rect(topleft=(TILE_WIDTH * object.pos_x, TILE_HEIGHT * object.pos_y))

    # проверка на столкновение по новым координатам
    collision = pygame.sprite.spritecollideany(object, sprite_group)

    # возвращение к начальным коодинатам
    object.pos_x = pos_x
    object.pos_y = pos_y

    # применение начальных координат
    object.rect = object.image.get_rect(topleft=(TILE_WIDTH * object.pos_x, TILE_HEIGHT * object.pos_y))
    return collision


# базовый класс для всех объектов в игре
class Object(pygame.sprite.Sprite):
    def __init__(self, groups, type, pos_x, pos_y, chunk_pos_x, chunk_pos_y, alpha, columns, rows, number_of_strokes):
        # groups - группы спрайтов, к которым принадлежит спрайт
        # alpha - для картинок с прозрачыми пикселями
        # columns - максимальное количество кадров среди всех анимаций спрайтов
        # rows - количество спрайтов

        super().__init__(*groups)
        # название спрайта. Нужно для того, чтобы связывать объект и то, что из него можно добыть
        self.type = type[:-4]

        # координаты левого верхнего угла спрайта внутри чанка
        self.pos_x = pos_x
        self.pos_y = pos_y

        # координаты чанка, в котором находится спрайт
        self.chunk_pos_x = chunk_pos_x
        self.chunk_pos_y = chunk_pos_y

        # массив картинок, из которых состоят анимации. Каждая анимация идёт по порядку сверху вниз, если посмотреть
        # файл со спрайтом
        self.frames = []

        # количество ударов, нанесённых по объектов
        self.hit_points = 0

        # количество ударов, которое может выдержать объект
        self.number_of_strokes = number_of_strokes

        # нарезка спрайта на куски для анимаций
        self.cut_sheet(load_image(type, alpha=alpha), columns, rows)

        self.image = self.frames[self.hit_points]
        self.rect = self.image.get_rect(topleft=(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y))

    def get_pos(self):
        pos = (self.pos_x, self.pos_y)
        return pos

    def update_chunk_pos(self, chunk_pos_x, chunk_pos_y):
        self.chunk_pos_x = chunk_pos_x
        self.chunk_pos_y = chunk_pos_y

    # метод для нарезки спрайта на кадры для анимации
    def cut_sheet(self, sheet, columns, rows):
        # sheet - спрайт

        # прямоугольник размером с 1 кадр анимации
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                # координаты левого верхнего угла кадра
                frame_location = (self.rect.w * i, self.rect.h * j)

                # добавление кадра в массив кадров
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, object_girds):
        # object_girds - двумерный массив значений, соответствующих объектам. Нужен только, если объект уничтожен,
        # чтобы удалить его оттуда

        self.hit_points += 1
        is_destroyed = False

        # если количество ударов становиться больше максимального количества ударов
        if self.hit_points > self.number_of_strokes:
            # удаление объекта из массива. Так как значение -1 не соответствует ни одному объекту
            object_girds[self.chunk_pos_y + self.pos_y][self.chunk_pos_x + self.pos_x] = -1
            is_destroyed = True

            # удаление объекта из игры
            self.kill()
        else:
            # если количество ударов меньше максимального, то меняется кадр анимации
            self.image = self.frames[self.hit_points]
        return object_girds, is_destroyed

    def check_collision(self, sprite_group, width, height):
        # sprite_group - группа спрайтов, с которой проверяется столкновение
        # width - размер экрана по x
        # height - размер экрана по y

        # максимальное количество тайлов, которое может поместиться на экране по x и по y
        chunk_size_x = width // TILE_WIDTH
        chunk_size_y = height // TILE_HEIGHT

        # проверка на столкновение
        if pygame.sprite.spritecollideany(self, sprite_group):
            return True

        # если объект находится на тайле, граничащем с тайлом из другого чанка, то вызывается эта функция. Подробнее о
        # её работе можно прочитать внутри этой функции
        if self.pos_x == 0:
            if check_collision_at_the_border(LEFT, chunk_size_x, self, sprite_group):
                return True
        if self.pos_x == chunk_size_x - 1:
            if check_collision_at_the_border(RIGHT, chunk_size_x, self, sprite_group):
                return True
        if self.pos_y == 0:
            if check_collision_at_the_border(UP, chunk_size_y, self, sprite_group):
                return True
        if self.pos_y == chunk_size_y - 1:
            if check_collision_at_the_border(DOWN, chunk_size_y, self, sprite_group):
                return True

        # если столкновения так и не произошло
        return False


class InventoryItem(Object):
    def __init__(self, item_groups, item_type, pos_x, pos_y, chunk_pos_x=None, chunk_pos_y=None):
        super().__init__(item_groups, item_type, pos_x, pos_y, chunk_pos_x, chunk_pos_y, True, 1, 1, 1)

        # количество объектов внутри одного. То-есть стак
        self.amount = 0
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def update_chunk_pos(self, chunk_pos_x, chunk_pos_y):
        self.chunk_pos_x = chunk_pos_x
        self.chunk_pos_y = chunk_pos_y

    def update_pos(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y

    # метод для отрисовки количества предметов на экране
    def draw_amount(self, screen, pos_x, pos_y):
        print_text(screen, pos_x, pos_y + 12, f"x{self.amount}", (0, 0, 0), font_size=7)


class Tile(Object):
    def __init__(self, tile_groups, tile_type, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(tile_groups, tile_type, pos_x, pos_y, chunk_x, chunk_y, False, 1, 1, 1)


class Tree(Object):
    def __init__(self, object_groups, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(object_groups, "tree.png", pos_x, pos_y, chunk_x, chunk_y, True, 1, 1, 1)


class Boulder(Object):
    def __init__(self, object_groups, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(object_groups, "stone.png", pos_x, pos_y, chunk_x, chunk_y, True, 6, 1, 5)


class Stone(InventoryItem):
    def __init__(self, item_groups, pos_x, pos_y):
        super().__init__(item_groups, "inventory_stone.png", pos_x, pos_y)
        self.type = "stone"


class House(Object):
    def __init__(self, object_groups, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(object_groups, "house.png", pos_x, pos_y, chunk_x, chunk_y, True, 2, 1, 3)
