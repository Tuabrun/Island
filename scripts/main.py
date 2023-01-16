import pygame
from pygame.locals import *

from file_directory import file_directory
from load_image import load_image
from cycles import game_cycle, show_menu


if __name__ == '__main__':
    TILE_WIDTH = TILE_HEIGHT = 96
    FPS = 60
    SPEED = 3
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"

    pygame.init()

    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.music.load(file_directory("sounds", "sea_sound.mp3"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    step_sound = pygame.mixer.Sound(file_directory("sounds", "sand_step.wav"))
    click_sound = pygame.mixer.Sound(file_directory("sounds", "click.wav"))
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

    program_icon = load_image("icon.png")
    pygame.display.set_icon(program_icon)

    while True:
        start_game = False
        if not start_game:
            start_game = show_menu(screen)
        if start_game:
            start_game = game_cycle(screen, width, height, step_sound)
