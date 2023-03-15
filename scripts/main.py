import pygame
from pygame.locals import *
import os

from file_directory import file_directory
from load_image import load_sprites
from cycles import game_cycle, menu_cycle


if __name__ == '__main__':
    # размеры тайла
    TILE_WIDTH = TILE_HEIGHT = 96

    pygame.init()

    # это тебе коментировать
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.music.load(file_directory("data/sounds/sea_sound.mp3"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    step_sound = pygame.mixer.Sound(file_directory("data/sounds/sand_step.wav"))
    click_sound = pygame.mixer.Sound(file_directory("data/sounds/click.wav"))
    step_sound.set_volume(0.3)

    info_object = pygame.display.Info()
    # ширина экрана
    width = info_object.current_w // TILE_WIDTH * TILE_WIDTH
    # высота экрана
    height = info_object.current_h // TILE_HEIGHT * TILE_HEIGHT

    # создание окна
    flags = FULLSCREEN | DOUBLEBUF
    screen = pygame.display.set_mode((width, height), flags)
    screen.set_alpha(None)

    sprites = load_sprites()

    # загрузка иконки
    program_icon = sprites["icon"]
    # применение иконки
    pygame.display.set_icon(program_icon)

    while True:
        # переменная, показывающая идёт ли игровой цикл
        start_game = False
        # если игровой цикл не идёт, то запускается цикл меню
        if not start_game:
            # при завершении игрового цикла возврашается True
            start_game = menu_cycle(screen, sprites, click_sound)
        # если игровой цикл идёт
        if start_game:
            # с помощью библиотеки os из директории, в которой находится main.py, программа поднимается на папку выше
            # а потом опускается в папку saves
            os.chdir("..")
            os.chdir("saves")
            # если папка с сохраниением не пустая
            if os.listdir():
                # берётся папка сохранения с самым большим номером
                save_number = max(list(map(int, os.listdir())))
                # запуск игрового цикла с выбранным сохранением
                start_game = game_cycle(screen, width, height, save_number, sprites, step_sound)
