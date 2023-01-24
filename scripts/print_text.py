import pygame

from file_directory import file_directory


def print_text(screen, x, y, message, font_color=(0, 0, 0),
               font_type=file_directory("fonts", "text.ttf"), font_size=30):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
