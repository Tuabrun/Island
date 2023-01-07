import pygame

from load_image import load_image


class Creature(pygame.sprite.Sprite):
    def __init__(self, creature_group, creature_type, pos_x, pos_y):
        super().__init__(creature_group)
        self.image = load_image(creature_type, alpha=True)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.motion_x = self.motion_y = None


class Hero(pygame.sprite.Sprite):
    def __init__(self, hero_group, screen_width, screen_height):
        super().__init__(hero_group)
        self.image = load_image("hero.png", alpha=True)
        self.rect = self.image.get_rect(topleft=(screen_width // 2, screen_height // 2))

    def udate(self, tile_group, direction_x, direction_y, hero_x, hero_y):
        sprites = pygame.sprite.spritecollide(self, tile_group, False)
        stop_motion = [False, False]
        if sprites:
            for sprite in sprites:
                print(sprite.get_pos())
                if direction_y == "up" and sprite.get_pos()[1] < hero_y and sprite.get_pos()[0] == hero_x:
                    stop_motion[1] = True
                if direction_y == "down" and sprite.get_pos()[1] > hero_y and sprite.get_pos()[0] == hero_x:
                    stop_motion[1] = True
                if direction_x == "right" and sprite.get_pos()[0] > hero_x and sprite.get_pos()[1] == hero_y:
                    stop_motion[0] = True
                if direction_x == "left" and sprite.get_pos()[0] < hero_x and sprite.get_pos()[1] == hero_y:
                    stop_motion[0] = True
        return stop_motion
