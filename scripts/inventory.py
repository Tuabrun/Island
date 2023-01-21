import pygame

from load_image import load_image
from objects import InventoryItem


def initialization_items(interface_group, item_group, hot_bar):
    inventory_stone = InventoryItem([interface_group, item_group], "inventory_stone.png",
                                    hot_bar.cell_x, hot_bar.cell_y)


class InterfaceElements(pygame.sprite.Sprite):
    def __init__(self, interface_group, interface_type):
        super().__init__(interface_group)
        self.image = load_image(interface_type)


class HotBar(InterfaceElements):
    def __init__(self, interface_group, true_width, true_height):
        super().__init__(interface_group, "hot_bar.png")
        self.rect = self.image.get_rect(center=(true_width // 2, true_height - 40))
        self.cell_x = true_width // 2 - 208 + 184
        self.cell_y = true_height - 40

    def draw(self, inventory):
        for item in inventory:
            if item[0] is not None:
                if item[1] == 0:
                    continue
                if item[1] < 5:
