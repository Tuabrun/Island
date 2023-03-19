import pygame

import objects

from constants import TILE_WIDTH, TILE_HEIGHT, RIGHT, LEFT, UP, DOWN, STACK


# класс, необходимый для заполнения пустых ячеек инвентаря
class EmptyCell:
    def __init__(self):
        self.type = None
        self.amount = 0


class Creature(pygame.sprite.Sprite):
    def __init__(self, creature_group, sprites, creature_type, speed, size_x, size_y,
                 creature_chunk, pos_x, pos_y, columns, rows):
        super().__init__(creature_group)
        self.speed = speed

        self.size_x = size_x
        self.size_y = size_y

        self.creature_chunk = creature_chunk

        self.pos_x = pos_x
        self.pos_y = pos_y

        # массив картинок, из которых состоят анимации. Каждая анимация идёт по порядку сверху вниз, если посмотреть
        # файл со спрайтом
        self.frames = []
        # нарезка спрайта на куски для анимаций
        self.cut_sheet(sprites[creature_type], columns, rows)

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(pos_x, pos_y))

    # доработать случай столкновения с несколькими объектами сразу !!!!!!
    def make_stop(self, sprite_group, direction_x, direction_y, creature_x, creature_y, stop_motion):
        # sprite_groups_chunks - группа спрайтов, с которой проверяется столкновение
        # direction_x - направление движения по x
        # direction_y - направление движения по y
        # hero_x - координаты по x
        # hero_y - координаты по y
        # stop_motion - массив, содержащий ограниченные направления движения

        # координаты тайла, в котором находится левый верхний угол персонажа
        creature_tile_x = creature_x // TILE_WIDTH
        creature_tile_y = creature_y // TILE_HEIGHT

        # кортеж, содержащий координаты левого верхнего угла
        topleft = (creature_x, creature_y)

        # обновление координатов персонажа
        self.rect = self.image.get_rect(topleft=topleft)

        # проверка на столкновение
        sprites = pygame.sprite.spritecollide(self, sprite_group, False)
        if sprites:
            # перебор каждого спрайта
            for sprite in sprites:
                # программа проверяет столкновение лишь с объектами на определённых тайлах.
                # нулевой тайл по x или y - это тот-же тайл, в котором находится персонаж, а, например, тайл -1
                # по x - это тайл находящийся на 1 тайл правее
                checked_tiles_x = [0]
                checked_tiles_y = [0]

                # если правый нижний угол персонажа находится на тайле правее, то в массив добавляется проверка на
                # столкновение с объектами из правого тайла
                if creature_tile_x < (creature_x + self.size_x - self.speed - 1) // TILE_WIDTH:
                    checked_tiles_x.append(-1)

                # если правый нижний угол персонажа находится на тайле ниже, то в массив добавляется проверка на
                # столкновение с объектами из нижнего тайла
                if creature_tile_y < (creature_y + self.size_x - self.speed - 1) // TILE_HEIGHT:
                    checked_tiles_y.append(-1)

                # если левый верхний угол персонажа находится на тайле левее, то из массива удаляется проверка на
                # столкновение с объектами из тайла, на ктотором находится левый угол персонажа
                if creature_tile_x < (creature_x + self.speed + 1) // TILE_WIDTH:
                    checked_tiles_x.remove(0)

                # если левый верхний угол персонажа находится на тайле выше, то из массива удаляется проверка на
                # столкновение с объектами из тайла, на ктотором находится левый угол персонажа
                if creature_tile_y < (creature_y + self.speed + 1) // TILE_HEIGHT:
                    checked_tiles_y.remove(0)

                if direction_x == RIGHT:
                    if creature_tile_x < sprite.get_pos()[0] and \
                            creature_tile_y - sprite.get_pos()[1] in checked_tiles_y:
                        stop_motion[0] = RIGHT
                if direction_x == LEFT:
                    if creature_tile_x >= sprite.get_pos()[0] and \
                            creature_tile_y - sprite.get_pos()[1] in checked_tiles_y:
                        stop_motion[0] = LEFT
                if direction_y == UP:
                    if creature_tile_y >= sprite.get_pos()[1] and \
                            creature_tile_x - sprite.get_pos()[0] in checked_tiles_x:
                        stop_motion[1] = UP
                if direction_y == DOWN:
                    if creature_tile_y < sprite.get_pos()[1] and \
                            creature_tile_x - sprite.get_pos()[0] in checked_tiles_x:
                        stop_motion[1] = DOWN
        return stop_motion

    def check_collision(self, sprite_groups, direction_x, direction_y, creature_x, creature_y, width, height):
        pos_x = creature_x % width
        pos_y = creature_y % height
        chunk_size_x = width // TILE_WIDTH - 1
        chunk_size_y = height // TILE_HEIGHT - 1
        stop_motion = [False, False]
        hero_tile_x = pos_x // TILE_WIDTH
        hero_tile_y = pos_y // TILE_HEIGHT
        for sprite_group in sprite_groups:
            stop_motion = self.make_stop(sprite_group[self.creature_chunk], direction_x,
                                         direction_y, pos_x, pos_y, stop_motion)
            creature_chunk = None
            if hero_tile_x in [0, chunk_size_x]:
                if hero_tile_x == 0 and self.creature_chunk not in [0, 3, 6]:
                    pos_x = pos_x + width
                    creature_chunk = self.creature_chunk - 1
                if hero_tile_x == chunk_size_x and self.creature_chunk not in [2, 5, 8]:
                    pos_x = pos_x - width
                    creature_chunk = self.creature_chunk + 1
                stop_motion = self.make_stop(sprite_group[creature_chunk], direction_x,
                                             direction_y, pos_x, pos_y, stop_motion)
                pos_x = creature_x % width

            if hero_tile_y in [0, chunk_size_y]:
                if hero_tile_y == 0 and self.creature_chunk not in [0, 1, 2]:
                    pos_y = pos_y + height
                    creature_chunk = self.creature_chunk - 3
                if hero_tile_y == chunk_size_y and self.creature_chunk not in [6, 7, 8]:
                    pos_y = pos_y - height
                    creature_chunk = self.creature_chunk + 3
                stop_motion = self.make_stop(sprite_group[creature_chunk], direction_x,
                                             direction_y, pos_x, pos_y, stop_motion)
                pos_y = creature_y % height
        return stop_motion

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Hero(Creature):
    def __init__(self, hero_group, sprites, speed, hero_size_x, hero_size_y):
        super().__init__(hero_group, sprites, "hero", speed, hero_size_x, hero_size_y, 4, 0, 0, 9, 4)
        # то, что находится в руках персонажа
        self.what_is_in_hands = "pickaxe"

        # то, что находится в ячейках инвентаря
        self.inventory = [EmptyCell(), EmptyCell(), EmptyCell(), EmptyCell()]

        self.update("run", RIGHT, 0)

    # пока не буду писать коментарии, потому что наверсняка переделаем эту функцию
    def update_inventory(self, item_groups, sprites, hot_bar, item):
        cell_number = 0
        free_cell = False
        add_item = False
        while cell_number < 4:
            if self.inventory[cell_number].object_type == item and self.inventory[cell_number].amount < STACK:
                add_item = True
                break
            if self.inventory[cell_number].type is None:
                free_cell = True
                break
            cell_number += 1
        if free_cell:
            if item == "stone":
                item = objects.Stone([item_groups], sprites, hot_bar.cell_x + 64 * cell_number, hot_bar.cell_y)
            self.inventory[cell_number] = item
        if free_cell or add_item:
            self.inventory[cell_number].amount += 1

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
