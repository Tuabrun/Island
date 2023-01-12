import pygame

from load_image import load_image

TILE_WIDTH = TILE_HEIGHT = 96


class Hero(pygame.sprite.Sprite):
    def __init__(self, hero_group):
        super().__init__(hero_group)
        self.frames = []
        self.cut_sheet(load_image("hero.png", alpha=True), 9, 4)
        self.update("run", "right", 0)

    def get_image(self):
        return self.image

    def make_stop_motion(self, sprite_group, direction_x, direction_y, hero_x, hero_y, stop_motion):
        hero_tile_x = hero_x // TILE_WIDTH
        hero_tile_y = hero_y // TILE_HEIGHT
        topleft = (hero_x, hero_y)
        self.rect = self.image.get_rect(topleft=topleft)
        sprites = pygame.sprite.spritecollide(self, sprite_group, False)
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

    def check_collision(self, sprite_group, direction_x, direction_y, hero_x, hero_y, width, height):
        chunk_size_x = width // TILE_WIDTH - 1
        chunk_size_y = height // TILE_HEIGHT - 1
        i = 4
        stop_motion = [False, False]
        hero_tile_x = hero_x // TILE_WIDTH
        hero_tile_y = hero_y // TILE_HEIGHT

        stop_motion = self.make_stop_motion(sprite_group[i], direction_x, direction_y, hero_x, hero_y, stop_motion)

        if hero_tile_x in [0, chunk_size_x]:
            if hero_tile_x == 0:
                hero_x += width
                i = 3
            if hero_tile_x == chunk_size_x:
                hero_x -= width
                i = 5
            stop_motion = self.make_stop_motion(sprite_group[i], direction_x, direction_y, hero_x, hero_y, stop_motion)

        if hero_tile_y in [0, chunk_size_y]:
            if hero_tile_y == 0:
                hero_y += height
                i = 1
            if hero_tile_y == chunk_size_y:
                hero_y -= height
                i = 7
            stop_motion = self.make_stop_motion(sprite_group[i], direction_x, direction_y, hero_x, hero_y, stop_motion)
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
            if direction == "right":
                self.image = self.frames[frame]
            if direction == "left":
                self.image = pygame.transform.flip(self.frames[frame], True, False)
            if direction == "up":
                if frame != 0:
                    frame = frame % 4 + 1
                self.image = self.frames[frame + 9]
            if direction == "down":
                self.image = self.frames[frame]
        if action == "cut_down":
            if frame != 0:
                frame = frame % 6 + 1
            if direction == "right":
                self.image = self.frames[frame + 18]
            if direction == "left":
                self.image = pygame.transform.flip(self.frames[frame + 21], True, False)
        if action == "mine":
            if frame != 0:
                frame = frame % 6 + 1
            if direction == "right":
                self.image = self.frames[frame + 27]
            if direction == "left":
                self.image = pygame.transform.flip(self.frames[frame + 32], True, False)


class Creature(pygame.sprite.Sprite):
    def __init__(self, creature_group, creature_type, pos_x, pos_y):
        super().__init__(creature_group)
        self.image = load_image(creature_type, alpha=True)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.motion_x = self.motion_y = None
