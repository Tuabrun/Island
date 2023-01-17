import pygame

from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96
SPEED = 3
RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"


class Hero(pygame.sprite.Sprite):
    def __init__(self, hero_group):
        super().__init__(hero_group)
        self.frames = []
        self.what_is_in_hands = "pickaxe"
        self.cut_sheet(load_image("hero.png", alpha=True), 9, 4)
        self.update("run", RIGHT, 0)

    def get_image(self):
        return self.image

    def make_stop(self, sprite_group, direction_x, direction_y, hero_x, hero_y, stop_motion):
        hero_tile_x = hero_x // TILE_WIDTH
        hero_tile_y = hero_y // TILE_HEIGHT
        topleft = (hero_x, hero_y)
        self.rect = self.image.get_rect(topleft=topleft)
        sprites = pygame.sprite.spritecollide(self, sprite_group, False)
        if sprites:
            for sprite in sprites:
                checked_tiles_x = [0]
                checked_tiles_y = [0]
                if hero_tile_x < (hero_x + 48 - SPEED - 1) // TILE_WIDTH:
                    checked_tiles_x.append(-1)
                if hero_tile_y < (hero_y + 48 - SPEED - 1) // TILE_HEIGHT:
                    checked_tiles_y.append(-1)
                if hero_tile_x < (hero_x + SPEED + 1) // TILE_WIDTH:
                    checked_tiles_x.remove(0)
                if hero_tile_y < (hero_y + SPEED + 1) // TILE_HEIGHT:
                    checked_tiles_y.remove(0)
                if direction_x == RIGHT:
                    if hero_tile_x < sprite.get_pos()[0] and hero_tile_y - sprite.get_pos()[1] in checked_tiles_y:
                        stop_motion[0] = RIGHT
                if direction_x == LEFT:
                    if hero_tile_x >= sprite.get_pos()[0] and hero_tile_y - sprite.get_pos()[1] in checked_tiles_y:
                        stop_motion[0] = LEFT
                if direction_y == UP:
                    if hero_tile_y >= sprite.get_pos()[1] and hero_tile_x - sprite.get_pos()[0] in checked_tiles_x:
                        stop_motion[1] = UP
                if direction_y == DOWN:
                    if hero_tile_y < sprite.get_pos()[1] and hero_tile_x - sprite.get_pos()[0] in checked_tiles_x:
                        stop_motion[1] = DOWN
        return stop_motion

    def check_collision(self, sprite_groups, direction_x, direction_y, hero_x, hero_y, width, height):
        pos_x = hero_x % width
        pos_y = hero_y % height
        chunk_size_x = width // TILE_WIDTH - 1
        chunk_size_y = height // TILE_HEIGHT - 1
        stop_motion = [False, False]
        hero_tile_x = pos_x // TILE_WIDTH
        hero_tile_y = pos_y // TILE_HEIGHT
        for sprite_group in sprite_groups:
            i = 4
            stop_motion = self.make_stop(sprite_group[i], direction_x, direction_y, pos_x, pos_y, stop_motion)

            if hero_tile_x in [0, chunk_size_x]:
                if hero_tile_x == 0:
                    pos_x = pos_x + width
                    i = 3
                if hero_tile_x == chunk_size_x:
                    pos_x = pos_x - width
                    i = 5
                stop_motion = self.make_stop(sprite_group[i], direction_x, direction_y, pos_x, pos_y, stop_motion)
                pos_x = hero_x % width

            if hero_tile_y in [0, chunk_size_y]:
                if hero_tile_y == 0:
                    pos_y = pos_y + height
                    i = 1
                if hero_tile_y == chunk_size_y:
                    pos_y = pos_y - height
                    i = 7
                stop_motion = self.make_stop(sprite_group[i], direction_x, direction_y, pos_x, pos_y, stop_motion)
                pos_y = hero_y % height
        return stop_motion

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, action, direction, frame):
        if action == "run":
            if frame != 0:
                frame = frame % 8 + 1
            if direction == RIGHT:
                self.image = self.frames[frame]
            if direction == LEFT:
                self.image = pygame.transform.flip(self.frames[frame], True, False)
            if direction == UP:
                if frame != 0:
                    frame = frame % 4 + 1
                self.image = self.frames[frame + 9]
            if direction == DOWN:
                self.image = self.frames[frame]
        if action == "cut_down":
            if frame != 0:
                frame = frame % 6 + 1
            if direction == RIGHT:
                self.image = self.frames[frame + 18]
            if direction == LEFT:
                self.image = pygame.transform.flip(self.frames[frame + 18], True, False)
        if action == "mine":
            if frame != 0:
                frame = frame % 6 + 1
            if direction == RIGHT:
                self.image = self.frames[frame + 27]
            if direction == LEFT:
                self.image = pygame.transform.flip(self.frames[frame + 27], True, False)

    def find_nearest_sprite(self, all_sprite_groups, hero_x, hero_y, width, height):
        nearest_sprite = [None, 10000, 10000]
        sprite_groups = None
        hero_x = width + hero_x
        hero_y = height + hero_y
        if self.what_is_in_hands is None:
            return nearest_sprite
        if self.what_is_in_hands == "pickaxe":
            sprite_groups = all_sprite_groups.for_extraction_with_pickaxe_groups
        if self.what_is_in_hands == "axe":
            sprite_groups = all_sprite_groups.for_extraction_with_axe_groups
        for chunk_y in range(3):
            for chunk_x in range(3):
                for sprite in sprite_groups[chunk_x + chunk_y * 3]:
                    distance_x = hero_x - sprite.get_pos()[0] * TILE_WIDTH - chunk_x * width
                    distance_y = hero_y - sprite.get_pos()[1] * TILE_HEIGHT - chunk_y * height
                    nearest_sprite_distance_x = hero_x - nearest_sprite[1]
                    nearest_sprite_distance_y = hero_y - nearest_sprite[2]
                    if distance_x < 0:
                        distance_x *= -1
                    if distance_y < 0:
                        distance_y *= -1
                    if nearest_sprite_distance_x < 0:
                        nearest_sprite_distance_x *= -1
                    if nearest_sprite_distance_y < 0:
                        nearest_sprite_distance_y *= -1
                    if nearest_sprite_distance_x + nearest_sprite_distance_y > distance_x + distance_y:
                        pos_x = sprite.get_pos()[0] * TILE_WIDTH + chunk_x * width
                        pos_y = sprite.get_pos()[1] * TILE_HEIGHT + chunk_y * height
                        nearest_sprite = [sprite, pos_x, pos_y]
        nearest_sprite[1] -= hero_x
        nearest_sprite[2] -= hero_y
        return nearest_sprite


class Creature(pygame.sprite.Sprite):
    def __init__(self, creature_group, creature_type, pos_x, pos_y):
        super().__init__(creature_group)
        self.image = load_image(creature_type, alpha=True)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.motion_x = self.motion_y = None
