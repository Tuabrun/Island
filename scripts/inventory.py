import pygame

from load_image import load_image


class InterfaceElements(pygame.sprite.Sprite):
    def __init__(self, interface_group, interface_type, true_width, true_height):
        super().__init__(interface_group)
        self.image = load_image(interface_type)


class FinishWindow(InterfaceElements):
    def __init__(self, interface_group, true_width, true_height):
        super().__init__(interface_group, "frame.png", true_width, true_height)
        self.rect = self.image.get_rect(center=(true_width // 2, true_height // 2))


class HotBar(InterfaceElements):
    def __init__(self, interface_group, true_width, true_height):
        super().__init__(interface_group, "hot_bar.png", true_width, true_height)
        self.rect = self.image.get_rect(center=(true_width // 2, true_height - 40))
        self.cell_x = true_width // 2 - 208 + 184
        self.cell_y = true_height - 40
