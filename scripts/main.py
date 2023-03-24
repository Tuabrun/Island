import pygame
from pygame.locals import *
import os

from file_directory import file_directory
from load_image import load_sprites
from cycles import game_cycle, menu_cycle

from constants import TILE_WIDTH, TILE_HEIGHT

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    # это тебе коментировать
    click_sound = pygame.mixer.Sound(file_directory("data/sounds/click.wav"))

    info_object = pygame.display.Info()
    # ширина экрана
    width = info_object.current_w // TILE_WIDTH * TILE_WIDTH + 10
    # высота экрана
    height = info_object.current_h // TILE_HEIGHT * TILE_HEIGHT + 10

    # создание окна
    flags = FULLSCREEN | DOUBLEBUF | SCALED | HWSURFACE
    screen = pygame.display.set_mode((width, height), flags)
    screen.set_alpha(None)

    sprites = load_sprites()

    # загрузка иконки
    program_icon = sprites["icon"]
    # применение иконкиц
    pygame.display.set_icon(program_icon)

    while True:
        menu_cycle(screen, sprites, click_sound)
        # с помощью библиотеки os из директории, в которой находится main.py, программа поднимается на папку выше
        # а потом опускается в папку saves
        os.chdir("..")
        os.chdir("saves")
        # если папка с сохраниением не пустая
        if os.listdir():
            # берётся папка сохранения с самым большим номером
            save_number = max(list(map(int, os.listdir())))
            # запуск игрового цикла с выбранным сохранением
            game_cycle(screen, width, height, save_number, sprites)
