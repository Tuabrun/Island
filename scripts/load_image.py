import pygame


def load_image(name, alpha=None, direction=None):  # функция для загрузки картинки
    fullname = open("../data/images/" + name, mode="rb").name
    screen = pygame.display

    # добавить сценарий отсутствия картинки!!!!!

    if alpha is not None:
        image = pygame.image.load(fullname).convert_alpha()
    else:
        image = pygame.image.load(fullname).convert()

    if direction is not None:
        image = pygame.transform.rotate(image, direction)
    return image
