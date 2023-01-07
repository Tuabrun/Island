import pygame

from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96


def make_stop_motion(sprite, sprite_group, direction_x, direction_y, hero_x, hero_y, stop_motion):
    hero_tile_x = hero_x // TILE_WIDTH
    hero_tile_y = hero_y // TILE_HEIGHT
    topleft = (hero_x, hero_y)
    sprite.rect = sprite.image.get_rect(topleft=topleft)
    sprites = pygame.sprite.spritecollide(sprite, sprite_group, False)
    checked_tiles_x = [0]
    checked_tiles_y = [0]
    if sprites:
        for sprite in sprites:
            if hero_tile_x < (hero_x + 44) // TILE_WIDTH:
                checked_tiles_x.append(-1)
            if hero_tile_y < (hero_y + 44) // TILE_HEIGHT:
                checked_tiles_y.append(-1)
            if direction_x == "right":
                if hero_tile_x < sprite.get_pos()[0] and hero_tile_y - sprite.get_pos()[1] in checked_tiles_y:
                    stop_motion[0] = "right"
            if direction_x == "left":
                if hero_tile_x >= sprite.get_pos()[0] and hero_tile_y - sprite.get_pos()[1] in checked_tiles_y:
                    stop_motion[0] = "left"
            if direction_y == "up":
                if hero_tile_y >= sprite.get_pos()[1] and hero_tile_x - sprite.get_pos()[0] in checked_tiles_x:
                    stop_motion[1] = "up"
            if direction_y == "down":
                if hero_tile_y < sprite.get_pos()[1] and hero_tile_x - sprite.get_pos()[0] in checked_tiles_x:
                    stop_motion[1] = "down"
    return stop_motion


class Creature(pygame.sprite.Sprite):
    def __init__(self, creature_group, creature_type, pos_x, pos_y):
        super().__init__(creature_group)
        self.image = load_image(creature_type, alpha=True)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.motion_x = self.motion_y = None


class Hero(pygame.sprite.Sprite):
    def __init__(self, hero_group):
        super().__init__(hero_group)
        self.image = load_image("hero.png", alpha=True)

    def get_image(self):
        return self.image

    def check_collision(self, sprite_group, direction_x, direction_y, hero_x, hero_y, width, height):
        chunk_size_x = width // TILE_WIDTH - 1
        chunk_size_y = height // TILE_HEIGHT - 1
        i = 4
        stop_motion = [False, False]
        hero_tile_x = hero_x // TILE_WIDTH
        hero_tile_y = hero_y // TILE_HEIGHT

        stop_motion = make_stop_motion(self, sprite_group[i], direction_x, direction_y, hero_x, hero_y, stop_motion)

        if hero_tile_x in [0, chunk_size_x]:
            if hero_tile_x == 0:
                hero_x += width
                i = 3
            if hero_tile_x == chunk_size_x:
                hero_x -= width
                i = 5
            stop_motion = make_stop_motion(self, sprite_group[i], direction_x, direction_y, hero_x, hero_y, stop_motion)

        if hero_tile_y in [0, chunk_size_y]:
            if hero_tile_y == 0:
                hero_y += height
                i = 1
            if hero_tile_y == chunk_size_y:
                hero_y -= height
                i = 7
            stop_motion = make_stop_motion(self, sprite_group[i], direction_x, direction_y, hero_x, hero_y, stop_motion)
        return stop_motion
