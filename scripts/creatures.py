import pygame

from load_image import load_image


class Creature(pygame.sprite.Sprite):
    def __init__(self, creature_group, creature_type):
        super().__init__(creature_group)
        self.image = load_image(creature_type, alpha=True)
        self.rect = self.image.get_rect().move(0, 0)


class Hero(Creature):
    def __init__(self, hero_group):
        super().__init__(hero_group, "hero.png")
