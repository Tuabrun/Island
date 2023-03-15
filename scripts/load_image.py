import pygame
import os


# функция для загрузки картинки
def load_sprite(name, alpha=None):
    # name - имя файла
    # alpha - для картинок с прозрачыми пикселями
    # direction - градус поворота картинки

    # путь к картинке
    fullname = open(name, mode="rb").name

    # добавить сценарий отсутствия картинки!!!!!

    if alpha is not None:
        # зашрузка картини с учётом параметра прозрачности пикселя
        sprite = pygame.image.load(fullname).convert_alpha()
    else:
        # зашрузка картини без учёта параметра прозрачности пикселя
        sprite = pygame.image.load(fullname).convert()
    return sprite


def load_sprites():
    all_sprites = {}
    os.chdir("..")
    os.chdir("data")
    os.chdir("images")
    for image in os.listdir():
        if image[:6] == "alpha_":
            all_sprites[image[6:-4]] = load_sprite(image, True)
        else:
            all_sprites[image[:-4]] = load_sprite(image)
    os.chdir("..")
    return all_sprites
