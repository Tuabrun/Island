import pygame

from file_directory import file_directory
from save_game import create_new_save


def print_text(message, x, y, screen, font_color=(0, 0, 0),
               font_type=file_directory("fonts", "text.ttf"), font_size=30):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))


class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inactive_color = (194, 255, 180)
        self.active_color = (35, 190, 3)

    def draw(self, screen, x, y, message, click_sound, action=None, font_size=30):
        is_click = False
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_color, (x, y, self.width, self.height))
            is_click = True
        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))
        print_text(message, x + 10, y + 10, screen, font_size)

        if is_click:
            if click[0] == 1:
                click_sound.play()
                pygame.time.delay(300)
                if action is not None:
                    if action == "quit":
                        pygame.quit()
                        quit()
                    if action == "change_cycle":
                        return False
                    if action == "new_world":
                        create_new_save()
                        return False
        return True