import pygame

from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96


class Tile(pygame.sprite.Sprite):
    def __init__(self, tiles_group, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = load_image(tile_type)
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

    def get(self):
        return self.image


class Object(pygame.sprite.Sprite):
    def __init__(self, object_group, object_type, object_width, objec_height, pos_x, pos_y):
        super().__init__(object_group)
        self.health_points = 100
        self.image = load_image(object_type, alpha=True)
        self.rect = self.image.get_rect().move(object_width * pos_x, objec_height * pos_y)

    def update(self, hit=False):
        if hit:
            self.health_points -= 20
        if self.health_points == 0:
            self.kill()


class Tree(Object):
    def __init__(self, object_group, pos_x, pos_y):
        super().__init__(object_group, "tree.png", 96, 96, pos_x, pos_y)


class Stone(Object):
    def __init__(self, object_group, pos_x, pos_y):
        super().__init__(object_group, "stone.png", 96, 96, pos_x, pos_y)
