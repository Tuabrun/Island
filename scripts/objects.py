import pygame

from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_groups, tile_type, pos_x, pos_y):
        super().__init__(*tile_groups)
        self.image = load_image(tile_type)
        self.rect = self.image.get_rect(topleft=(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y))
        self.pos_x = pos_x
        self.pos_y = pos_y

    def get_pos(self):
        pos = (self.pos_x, self.pos_y)
        return pos


class Object(pygame.sprite.Sprite):
    def __init__(self, object_group, object_type, pos_x, pos_y):
        super().__init__(object_group)
        self.health_points = 100
        self.image = load_image(object_type, alpha=True)
        self.rect = self.image.get_rect().move(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)

    def update(self, hit=False):
        if hit:
            self.health_points -= 20
        if self.health_points == 0:
            self.kill()


class Tree(Object):
    def __init__(self, object_group, pos_x, pos_y):
        super().__init__(object_group, "tree.png", pos_x, pos_y)


class Stone(Object):
    def __init__(self, object_group, pos_x, pos_y):
        super().__init__(object_group, "stone.png", pos_x, pos_y)
