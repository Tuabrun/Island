import pygame

from file_directory import file_directory


# функция для отрисовки текста на экране
def print_text(surface, x, y, message, font_color=(0, 0, 0),
               font_type=file_directory("data/fonts/text.ttf"), font_size=30):
    # surface - surface, на котором необходимо отрисовать текст
    # x - координата левого верхнего угла текста по x
    # y - координата левого верхнего угла текста по y
    # message - текст, который необходимо отрисовать
    # font_color - цвет текста в палитре RGB
    # font_type - используемый шрифт (находится в файле)
    # font_size - размер букв

    # загрузка шрифта и его размер
    font_type = pygame.font.Font(font_type, font_size)

    # это тебе коментировать
    text = font_type.render(message, True, font_color)

    # вывод текста на surface, координаты левого верхнего угла которого равны (x;y)
    surface.blit(text, (x, y))
