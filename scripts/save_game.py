import pygame
import os

from world import World

from constants import TILE_WIDTH, TILE_HEIGHT


def save_file(save_number, save_name, information):
    # save_number - номер папки сохранения
    # save_name - имя файла внутри папки с сохранением
    # information - массив информации, которую необходимо записать в файл

    # открытие или создание файла из-за его отсутствия в режиме записи
    positions = open(f"../saves/{save_number}/{save_name}", "w", encoding="utf8")

    # прохождение всех элементов массива
    for element in information:

        # конвертация значения элемента в массив строк
        y = list(map(str, element))

        # склеивание массива значений в сторку, где элементы разделены пробелом
        positions.write(" ".join(y) + "\n")

    # заверщение работы с файлом
    positions.close()


def save_game(save_number, world, hero_x, hero_y):
    # сохранение информации во всех файлах сохранения
    save_file(save_number, "tile_positions", world.tile_grids)
    save_file(save_number, "object_positions", world.object_grids)
    save_file(save_number, "hero_position", [[hero_x, hero_y, world.main_chunk_x, world.main_chunk_y]])


def create_new_save():
    info_object = pygame.display.Info()

    # размер экрана по x и по y
    width = info_object.current_w // TILE_WIDTH * TILE_WIDTH
    height = info_object.current_h // TILE_HEIGHT * TILE_HEIGHT

    # с помощью библиотеки os из директории, в которой находится save_game.py, программа поднимается на папку выше
    # а потом опускается в папку saves
    os.chdir("..")
    os.chdir("saves")

    # поиск папки сохранения с самым большим числом
    save_number = 0
    while True:
        # если папки с таким номером не существует, то цикл заверщает работу
        if not os.path.isdir(f"{save_number}"):
            break
        save_number += 1

    # создаётся папка с номером, который мы получили из цикла выше
    os.mkdir(f"{save_number}")

    # создаётся экземпляр класса world
    world = World(900, 450, 2, width, height)

    # для него создаётся мир
    world.create_world()

    # и наполняется объектами
    world.filling_the_world()

    # информация о новом мире сохраняется в папку, которую мы создали выше
    save_game(save_number, world, world.hero_x, world.hero_y)
