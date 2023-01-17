import pygame
import os

from world import World

TILE_WIDTH = TILE_HEIGHT = 96


def save_file(save_number, save_name, information):
    positions = open(f"../saves/{save_number}/{save_name}", "w", encoding="utf8")

    for y in information:
        y = list(map(str, y))
        positions.write(" ".join(y) + "\n")
    positions.close()


def save_game(save_number, world, hero_x, hero_y):
    save_file(save_number, "tile_positions", world.tile_grids)
    save_file(save_number, "object_positions", world.object_grids)
    save_file(save_number, "hero_position", [[hero_x, hero_y, world.main_chunk_x, world.main_chunk_y]])


def create_new_save():
    info_object = pygame.display.Info()
    # ширина экрана
    width = info_object.current_w // TILE_WIDTH * TILE_WIDTH
    # высота экрана
    height = info_object.current_h // TILE_HEIGHT * TILE_HEIGHT

    os.chdir("..")
    os.chdir("saves")
    save_number = 0
    while True:
        if not os.path.isdir(f"{save_number}"):
            break
        save_number += 1
    os.mkdir(f"{save_number}")

    world = World(900, 450, 2, width, height)
    world.create_world()
    world.filling_the_world()
    save_game(save_number, world, world.hero_x, world.hero_y)
