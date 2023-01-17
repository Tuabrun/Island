import pygame

from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96


class Object(pygame.sprite.Sprite):
    def __init__(self, groups, type, pos_x, pos_y, chunk_pos_x, chunk_pos_y, alpha, colums, rows, number_of_strokes):
        super().__init__(*groups)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.chunk_pos_x = chunk_pos_x
        self.chunk_pos_y = chunk_pos_y

        self.frames = []
        self.hit_points = 0
        self.number_of_strokes = number_of_strokes
        self.cut_sheet(load_image(type, alpha=alpha), colums, rows)
        self.image = self.frames[self.hit_points]
        self.rect = self.image.get_rect(topleft=(TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y))

    def get_pos(self):
        pos = (self.pos_x, self.pos_y)
        return pos

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, object_girds):
        self.hit_points += 1
        is_destroyed = False
        if self.hit_points > self.number_of_strokes:
            object_girds[self.chunk_pos_y + self.pos_y][self.chunk_pos_x + self.pos_x] = -1
            is_destroyed = True
            self.kill()
        else:
            self.image = self.frames[self.hit_points]
        return object_girds, is_destroyed

    def check_collision(self, sprite_group, width, height):
        chunk_size_x = width // TILE_WIDTH
        chunk_size_y = height // TILE_HEIGHT
        if pygame.sprite.spritecollideany(self, sprite_group):
            return True
        if self.pos_x == 0:
            self.pos_x += chunk_size_x
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            collision = pygame.sprite.spritecollideany(self, sprite_group)
            self.pos_x -= chunk_size_x
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            if collision:
                return True
        if self.pos_x == chunk_size_x - 1:
            self.pos_x -= chunk_size_x
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            collision = pygame.sprite.spritecollideany(self, sprite_group)
            self.pos_x += chunk_size_x
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            if collision:
                return True
        if self.pos_y == 0:
            self.pos_y += chunk_size_y
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            collision = pygame.sprite.spritecollideany(self, sprite_group)
            self.pos_y -= chunk_size_y
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            if collision:
                return True
        if self.pos_y == chunk_size_y - 1:
            self.pos_y -= chunk_size_y
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            collision = pygame.sprite.spritecollideany(self, sprite_group)
            self.pos_y += chunk_size_y
            self.rect = self.image.get_rect(topleft=(TILE_WIDTH * self.pos_x, TILE_HEIGHT * self.pos_y))
            if collision:
                return True
        return False


class Tile(Object):
    def __init__(self, tile_group, tile_type, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(tile_group, tile_type, pos_x, pos_y, chunk_x, chunk_y, False, 1, 1, 1)


class Tree(Object):
    def __init__(self, object_group, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(object_group, "tree.png", pos_x, pos_y, chunk_x, chunk_y, True, 1, 1, 1)


class Stone(Object):
    def __init__(self, object_group, pos_x, pos_y, chunk_x, chunk_y):
        super().__init__(object_group, "stone.png", pos_x, pos_y, chunk_x, chunk_y, True, 6, 1, 5)