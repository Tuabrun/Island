import pygame
from load_image import load_image

tile_width = tile_height = 32


class Tile(pygame.sprite.Sprite):
    def __init__(self, tiles_group, all_sprites, tile_type, pos_x, pos_y, direction=None):
        super().__init__(tiles_group, all_sprites)
        self.image = load_image(tile_type, direction)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
