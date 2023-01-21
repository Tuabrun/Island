import pygame
from load_image import load_image
from main import screen
import time

def print_text(message, x, y, font_color=(0,0,0), font_type='Samson.ttf', font_size=30):
    font_type = pygame.font.Font(font_type,font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))


class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inactive_color = (194,255,180)
        self.active_color = (35, 190, 3)
    def draw(self, x, y, message, action=None, font_size=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < self.width and y < mouse[1] < self.height:
            pygame.draw.rect(screen,self.active_color, (x, y, self.width, self.height))
            if click[0]==1 :
                #click_sound.play()
                pygame.time.delay(300)
                if action is not None:
                    action()
        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))

        print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)

def show_menu():
    menu_background = load_image('background.png')
    start_button = Button(300, 70)
    show = True

    while show:
        for event in pygame.event.get():
            # нажатие крестика в правом верхнем углу
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if vol > 0.0:
                        vol -= 0.1
                        pygame.mixer.music.set_volume(vol)
                if event.key == pygame.K_RIGHT:
                    if vol < 1.0:
                        vol += 0.1
                        pygame.mixer.music.set_volume(vol)
        screen.blit(menu_background, (0, 0))
        start_button.draw(300,200, 'Start game')

        pygame.display.update()
        pygame.time.Clock.tick(60)