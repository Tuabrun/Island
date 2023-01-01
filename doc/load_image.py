import pygame


def load_image(name, direction=None, colorkey=None):  # функция для загрузки картинки
    fullname = open("../data/images/" + name, mode="rb").name

    # добавить сценарий отсутствия картинки!!!!!

    image = pygame.image.load(fullname)
    if direction is not None:
        image = pygame.transform.rotate(image, direction)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image
