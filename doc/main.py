import pygame


if __name__ == '__main__':
    pygame.init()
    infoObject = pygame.display.Info()
    # ширина экрана
    width = infoObject.current_w
    #  высота экрана
    height = infoObject.current_h
    # создание окна
    pygame.display.set_mode((width, height))

    # основной игровой цикл
    running = True
    while running:
        for event in pygame.event.get():
            # нажатие крестика в правом верхнем углу
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()