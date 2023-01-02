import pygame
from pygame.locals import *

from map import World

if __name__ == '__main__':
    pygame.init()
    infoObject = pygame.display.Info()
    # ширина экрана
    width = infoObject.current_w
    #  высота экрана
    height = infoObject.current_h

    all_sprites = pygame.sprite.Group()
    chunks_group_of_sprites = []
    for _ in range(9):
        tiles_group = pygame.sprite.Group()
        chunks_group_of_sprites.append(tiles_group)

    tile_width = tile_height = 96

    # создание окна
    flags = FULLSCREEN | DOUBLEBUF
    screen = pygame.display.set_mode((width, height), flags)
    screen.set_alpha(None)

    FPS = 60  # число кадров в секунду
    clock = pygame.time.Clock()

    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    world = World(chunks_group_of_sprites, 900, 450, 2, width, height)
    spawn_x, spawn_y = world.create_world()
    world.draw()
    world.make_map()
    chunks = []
    for index in range(9):
        chunk = pygame.Surface((width, height)).convert()
        chunk.set_alpha(None)
        chunks.append(chunk)
        chunks_group_of_sprites[index].draw(chunks[index])

    camera_x, camera_y = -spawn_x - width // 2, -spawn_y - height // 2
    motion_x = motion_y = None

    # основной игровой цикл
    running = True
    while running:
        for event in pygame.event.get():
            # нажатие крестика в правом верхнем углу
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    motion_y = "up"
                if event.key == pygame.K_s:
                    motion_y = "down"
                if event.key == pygame.K_d:
                    motion_x = "right"
                if event.key == pygame.K_a:
                    motion_x = "left"
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_s]:
                    motion_y = None
                if event.key in [pygame.K_d, pygame.K_a]:
                    motion_x = None

        if motion_y == "up":
            camera_y += 5
        if motion_y == "down":
            camera_y -= 5
        if motion_x == "right":
            camera_x -= 5
        if motion_x == "left":
            camera_x += 5

        if camera_y + height // 2 > 0:
            chunks_group_of_sprites_copy = []
            for _ in range(9):
                tiles_group = pygame.sprite.Group()
                chunks_group_of_sprites_copy.append(tiles_group)

            for index in range(3, 9):
                chunks_group_of_sprites_copy[index] = chunks_group_of_sprites[index - 3]
            chunks_group_of_sprites = chunks_group_of_sprites_copy
            world.update(chunks_group_of_sprites, "up")
            for index in range(9):
                chunks_group_of_sprites[index].draw(chunks[index])
            camera_y = -height - height // 2

        if camera_y + height // 2 < -height:
            chunks_group_of_sprites_copy = []
            for _ in range(9):
                tiles_group = pygame.sprite.Group()
                chunks_group_of_sprites_copy.append(tiles_group)

            for index in range(6):
                chunks_group_of_sprites_copy[index] = chunks_group_of_sprites[index + 3]
            chunks_group_of_sprites = chunks_group_of_sprites_copy
            world.update(chunks_group_of_sprites, "down")
            for index in range(9):
                chunks_group_of_sprites[index].draw(chunks[index])
            camera_y = 0 - height // 2

        if camera_x + width // 2 < -width:
            chunks_group_of_sprites_copy = []
            for _ in range(9):
                tiles_group = pygame.sprite.Group()
                chunks_group_of_sprites_copy.append(tiles_group)

            for index in [0, 1, 3, 4, 6, 7]:
                chunks_group_of_sprites_copy[index] = chunks_group_of_sprites[index + 1]
            chunks_group_of_sprites = chunks_group_of_sprites_copy
            world.update(chunks_group_of_sprites, "right")

            for index in range(9):
                chunks_group_of_sprites[index].draw(chunks[index])
            camera_x = 0 - width // 2

        if camera_x + width // 2 > 0:
            chunks_group_of_sprites_copy = []
            for _ in range(9):
                tiles_group = pygame.sprite.Group()
                chunks_group_of_sprites_copy.append(tiles_group)

            for index in [1, 2, 4, 5, 7, 8]:
                chunks_group_of_sprites_copy[index] = chunks_group_of_sprites[index - 1]
            chunks_group_of_sprites = chunks_group_of_sprites_copy
            world.update(chunks_group_of_sprites, "left")
            for index in range(9):
                chunks_group_of_sprites[index].draw(chunks[index])
            camera_x = -width - width // 2

        screen.fill((0, 0, 0))
        for index_x in range(3):
            for index_y in range(3):
                screen.blit(chunks[index_x + 3 * index_y], (camera_x + width * index_x, camera_y + height * index_y))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
