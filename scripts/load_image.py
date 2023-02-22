import pygame


# функция для загрузки картинки
def load_image(name, alpha=None, direction=None):
    # name - имя файла
    # alpha - для картинок с прозрачыми пикселями
    # direction - градус поворота картинки

    # путь к картинке
    fullname = open("../data/images/" + name, mode="rb").name

    # добавить сценарий отсутствия картинки!!!!!

    if alpha is not None:
        # зашрузка картини с учётом параметра прозрачности пикселя
        image = pygame.image.load(fullname).convert_alpha()
    else:
        # зашрузка картини без учёта параметра прозрачности пикселя
        image = pygame.image.load(fullname).convert()

    if direction is not None:
        # поворот картинки на direction градусов
        image = pygame.transform.rotate(image, direction)
    return image
