import pygame

from load_image import load_sprite


# базовый класс для элементов интерфейса
class InterfaceElements(pygame.sprite.Sprite):
    def __init__(self, interface_group, sprites, interface_type):
        super().__init__(interface_group)
        self.image = sprites[interface_type]


# класс для всплывающих окон
class PopUpWindow(InterfaceElements):
    def __init__(self, interface_group, true_width, true_height):
        # true_width - реальные размеры экрана по x
        # true_height - реальные размеры экрана по y

        super().__init__(interface_group, "frame.png")
        self.rect = self.image.get_rect(center=(true_width // 2, true_height // 2))


# класс для хотбара (инвентаря)
class HotBar(InterfaceElements):
    def __init__(self, interface_group, sprites, true_width, true_height):
        # true_width - реальные размеры экрана по x
        # true_height - реальные размеры экрана по y

        super().__init__(interface_group, sprites, "hot_bar")
        self.rect = self.image.get_rect(center=(true_width // 2, true_height - 40))

        # координаты первой ячейки по x
        self.cell_x = true_width // 2 - 208 + 184
        # координаты первой ячейки по y
        self.cell_y = true_height - 40
