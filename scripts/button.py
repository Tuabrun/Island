import pygame

from save_game import create_new_save
from print_text import print_text


class Button:
    def __init__(self, width, height):
        # размер кнопки по x и по y
        self.width = width
        self.height = height

        # цвет кнопки по умолчанию
        self.inactive_color = (194, 255, 180)
        # цвет кнопки при наведении курсора
        self.active_color = (35, 190, 3)

    def draw(self, surface, x, y, message, click_sound, action=None, font_size=30):
        # surface - surface, на котором необходимо отрисовать кнопку
        # x - координата левого верхнего угла кнопки по x
        # y - координата левого верхнего угла кнопки по y
        # message - текст, который необходимо отрисовать на кнопке
        # click_sound - звук нажатия
        # action - действие, которое выполняется при нажатии кнопки
        # font_size - размер букв на кнопке

        # переменная, показывающая нажата ли кнопка
        is_click = False

        # получение координат мыши
        mouse = pygame.mouse.get_pos()
        # получение информации о нажатии кнопок мыши
        click = pygame.mouse.get_pressed()

        # если координаты курсора по x и по y находятся внутри кнопки
        if x < mouse[0] < (x + self.width) and y < mouse[1] < y + self.height:

            # перекрашивание цвета кнопки на цвет при наведении курсора
            pygame.draw.rect(surface, self.active_color, (x, y, self.width, self.height))

            # кнопка становится нажатой
            is_click = True
        else:
            # перекрашивание цвета кнопки на цвет по умолчанию
            pygame.draw.rect(surface, self.inactive_color, (x, y, self.width, self.height))

        # отрисовка текста на кнопке
        print_text(surface, x + 10, y + 10, message, font_size)

        # если клавиша нажата
        if is_click:
            # если нажата левая кнопка мыши
            if click[0] == 1:

                # проигрывание звука нажатия
                click_sound.play()

                # это тебе коментировать
                pygame.time.delay(300)
                if action is not None:
                    # действие выхода из игры
                    if action == "quit":
                        quit()

                    # действие отключения старого и активации нового цикла
                    # подробнее описано в функции menu_cycle в файле cycles.py
                    if action == "change_cycle":
                        return False

                    # действие отключения старого и активации нового цикла и создание новой папки с сохранением
                    if action == "new_world":
                        create_new_save()
                        return False

        # значение True позволяет продолжать работать игровому циклу, внутри которого отрисовывается эта кнопка
        return True
