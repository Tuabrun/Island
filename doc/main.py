import pygame

from map import World

if __name__ == '__main__':
    pygame.init()
    infoObject = pygame.display.Info()
    # ширина экрана
    width = infoObject.current_w
    #  высота экрана
    height = infoObject.current_h

    tiles_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    # создание окна
    screen = pygame.display.set_mode((width, height))

    FPS = 60  # число кадров в секунду
    clock = pygame.time.Clock()

    world = World(tiles_group, all_sprites, 144, 81, 2)
    spawn_x, spawn_y = world.create_world(width, height)
    sector_x, sector_y = world.draw(width, height)
    world.make_map()
    land = pygame.Surface((sector_x, sector_y))
    tiles_group.draw(land)
    camera_x, camera_y = -spawn_x - width // 2, -spawn_y - height // 2
    motion_x, motion_y = None, None

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
            camera_y += 10
        if motion_y == "down":
            camera_y -= 10
        if motion_x == "right":
            camera_x -= 10
        if motion_x == "left":
            camera_x += 10
        screen.fill((0, 0, 0))
        screen.blit(land, (camera_x, camera_y))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
