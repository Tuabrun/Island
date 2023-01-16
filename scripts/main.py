import pygame
from pygame.locals import *
from world import World
import creatures
from load_image import load_image


# класс для хранения и отрисовки групп спрайтов
class SpritesGroupsForChunks:
    def __init__(self):
        self.group_of_chunks = []
        self.group_of_objects = []
        self.group_of_water_tiles = []
        # каждая группа спрайтов повторяется 9 раз и передаётся в соответствующий массив
        # далее я поясню зачем это нужно
        for _ in range(9):
            tiles_group = pygame.sprite.Group()
            water_tiles_group = pygame.sprite.Group()
            objects_group = pygame.sprite.Group()
            self.group_of_chunks.append(tiles_group)
            self.group_of_water_tiles.append(water_tiles_group)
            self.group_of_objects.append(objects_group)

    def get_group_of_chunks_and_objects(self):
        return [self.group_of_chunks, self.group_of_objects]

    # метод для отрисовки групп спрайтов. Принимает на вход массив из surface
    # далее названием chunk будет называться surface размером с экран
    def draw(self, chunks):
        for sprite_group in self.get_group_of_chunks_and_objects():
            for i in range(9):
                sprite_group[i].draw(chunks[i])


if __name__ == '__main__':
    TILE_WIDTH = TILE_HEIGHT = 96
    SPEED = 3

    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    infoObject = pygame.display.Info()
    # ширина экрана
    width = infoObject.current_w // TILE_WIDTH * TILE_WIDTH
    # высота экрана
    height = infoObject.current_h // TILE_HEIGHT * TILE_HEIGHT

    sprite_groups = SpritesGroupsForChunks()
    hero_group = pygame.sprite.Group()

    # создание окна
    flags = FULLSCREEN | DOUBLEBUF
    screen = pygame.display.set_mode((width, height), flags)
    screen.set_alpha(None)

    FPS = 60  # число кадров в секунду
    clock = pygame.time.Clock()
    counter = -1

    # ограничение списка проверяемых событий для лучшей производительности
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    program_icon = load_image("icon.png")
    pygame.display.set_icon(program_icon)


    def file_directory(directory, name):
        file_directory = open(f"../data/{directory}/{name}", mode="rb").name
        return file_directory

    pygame.mixer.music.load(file_directory("sounds", "sea_sound.mp3"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    vol = 0.1
    step_sound = pygame.mixer.Sound(file_directory("sounds", "sand_step.wav"))
    click_sound = pygame.mixer.Sound(file_directory("sounds", "click.wav"))
    step_sound.set_volume(0.3)
    step_counter = 0

    world = World(sprite_groups, 900, 450, 2, width, height)
    # координаты персонажа В ЦЕНТРАЛЬНОМ ЧАНКЕ и создание мира
    # пояснение: в игре отрисовываются лишь 9 чанков, и в центральном чанке находится персонаж
    # как раз таки поэтому каждая группа спрайтов повторялатсь 9 раз. Каждой группе спрайтов соответствует свой чанк
    hero_pos_x, hero_pos_y = world.create_world()
    # создание объектов вроде камня
    world.filling_the_world()
    # присваивание тайлам и объектам соответствующие спрайты
    world.draw()
    # создание карты
    world.make_map()

    # создание чанков
    chunks = []
    for index in range(9):
        chunk = pygame.Surface((width, height)).convert()
        chunk.set_alpha(None)
        chunks.append(chunk)
    # отрисовка спрайтов на этих чанках
    sprite_groups.draw(chunks)

    hero = creatures.Hero(hero_group)
    direction = "right"

    # координаты центрального чанка на дисплее
    camera_x, camera_y = -hero_pos_x - width // 2, -hero_pos_y - height // 2
    # переменные, отвечающие за движение камеры
    motion_x = motion_y = None


    def print_text(message, x, y, font_color=(0, 0, 0), font_type=file_directory("fonts", "text.ttf"), font_size=30):
        font_type = pygame.font.Font(font_type, font_size)
        text = font_type.render(message, True, font_color)
        screen.blit(text, (x, y))


    class Button:
        def __init__(self, width, height):
            self.width = width
            self.height = height
            self.inactive_color = (194, 255, 180)
            self.active_color = (35, 190, 3)

        def draw(self, x, y, message, action_2=None, font_size=30):
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
                pygame.draw.rect(screen, self.active_color, (x, y, self.width, self.height))
                if click[0] == 1:
                    click_sound.play()
                    pygame.time.delay(300)
                    if action_2 is not None:
                        if action_2 == quit:
                            pygame.quit()
                            quit()
                        action_2()
            else:
                pygame.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height))

            print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)


    def start_game():
        global vol, counter, motion_x, motion_y, sprite_groups, hero_pos_y, hero_pos_x, step_counter, camera_y, \
            camera_x, direction

        running = True
        while running:
            print(counter)
            counter = (counter + 1) % 96
            frame_number = counter // 4 + 1

            for event in pygame.event.get():
                # нажатие крестика в правом верхнем углу
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if vol > 0.0:
                            vol -= 0.1
                            pygame.mixer.music.set_volume(vol)
                    if event.key == pygame.K_RIGHT:
                        if vol < 1.0:
                            vol += 0.1
                            pygame.mixer.music.set_volume(vol)


                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        motion_x = "right"
                    if event.key == pygame.K_a:
                        motion_x = "left"
                    if event.key == pygame.K_w:
                        motion_y = "up"
                    if event.key == pygame.K_s:
                        motion_y = "down"
                    if event.key == pygame.K_ESCAPE:
                        show_menu()
                direction = motion_x
                if motion_x is None:
                    direction = motion_y

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_d and motion_x == "right":
                        motion_x = None
                    if event.key == pygame.K_a and motion_x == "left":
                        motion_x = None
                    if event.key == pygame.K_w and motion_y == "up":
                        motion_y = None
                    if event.key == pygame.K_s and motion_y == "down":
                        motion_y = None

            motion = hero.check_collision(sprite_groups.group_of_water_tiles, motion_x, motion_y,
                                          hero_pos_x, hero_pos_y, width, height)
            if motion_x == "right" and motion[0] != "right":
                camera_x -= SPEED
                hero_pos_x += SPEED
                step_counter += 1
            if motion_x == "left" and motion[0] != "left":
                camera_x += SPEED
                hero_pos_x -= SPEED
                step_counter += 1
            if motion_y == "up" and motion[1] != "up":
                camera_y += SPEED
                hero_pos_y -= SPEED
                step_counter += 1
            if motion_y == "down" and motion[1] != "down":
                camera_y -= SPEED
                hero_pos_y += SPEED
                step_counter += 1
            if step_counter == 20:
                step_sound.play()
            elif step_counter>20:
                step_counter = 0
            if motion_x is None and motion_y is None:
                frame_number = 0
            hero.update("run", direction, frame_number)

            # дальше идут 4 похожих блока пока, поэтому поясю за все сразу
            # если центральный чанк полностью ущёл за границы экрана (тоесть координаты его верхнего левого угла
            # либо меньше размера экрана по x или по y, либо больше 0), то первые 3 чанка по направлению движения
            # камеры полностью обновляют свои группы спрайтов, а остальные 6 чанков меняют свои группы спрайтов
            # на группу спрайтов соседа по направлению движения камеры. Соответственно меняется и главный чанк по
            # направлению движения камеры. В конце все группы спрайтов отрисовываюся на своих чанках, а положение
            # камеры смещается к персонажу на главном чанке
            if camera_x + width // 2 < -width:
                sprite_groups_copy = SpritesGroupsForChunks()
                for index in [0, 1, 3, 4, 6, 7]:
                    for group_of_sprites in range(len(sprite_groups.get_group_of_chunks_and_objects())):
                        sprite_groups_copy.get_group_of_chunks_and_objects()[group_of_sprites][index] =\
                            sprite_groups.get_group_of_chunks_and_objects()[group_of_sprites][index + 1]
                    sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index + 1]
                sprite_groups = sprite_groups_copy
                world.update(sprite_groups, "right")
                sprite_groups.draw(chunks)
                camera_x = 0 - width // 2
                hero_pos_x = 0

            if camera_x + width // 2 > 0:
                sprite_groups_copy = SpritesGroupsForChunks()
                for index in [1, 2, 4, 5, 7, 8]:
                    for group_of_sprites in range(len(sprite_groups.get_group_of_chunks_and_objects())):
                        sprite_groups_copy.get_group_of_chunks_and_objects()[group_of_sprites][index] =\
                            sprite_groups.get_group_of_chunks_and_objects()[group_of_sprites][index - 1]
                    sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index - 1]
                sprite_groups = sprite_groups_copy
                world.update(sprite_groups, "left")
                sprite_groups.draw(chunks)
                camera_x = -width - width // 2
                hero_pos_x = width

            if camera_y + height // 2 > 0:
                sprite_groups_copy = SpritesGroupsForChunks()
                for index in range(3, 9):
                    for group_of_sprites in range(len(sprite_groups.get_group_of_chunks_and_objects())):
                        sprite_groups_copy.get_group_of_chunks_and_objects()[group_of_sprites][index] =\
                            sprite_groups.get_group_of_chunks_and_objects()[group_of_sprites][index - 3]
                    sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index - 3]
                sprite_groups = sprite_groups_copy
                world.update(sprite_groups, "up")
                sprite_groups.draw(chunks)
                camera_y = -height - height // 2
                hero_pos_y = height

            if camera_y + height // 2 < -height:
                sprite_groups_copy = SpritesGroupsForChunks()
                for index in range(6):
                    for group_of_sprites in range(len(sprite_groups.get_group_of_chunks_and_objects())):
                        sprite_groups_copy.get_group_of_chunks_and_objects()[group_of_sprites][index] =\
                            sprite_groups.get_group_of_chunks_and_objects()[group_of_sprites][index + 3]
                    sprite_groups_copy.group_of_water_tiles[index] = sprite_groups.group_of_water_tiles[index + 3]
                sprite_groups = sprite_groups_copy
                world.update(sprite_groups, "down")
                sprite_groups.draw(chunks)
                camera_y = 0 - height // 2
                hero_pos_y = 0

            # изменение положения всех чанков на дисплее
            for index_x in range(3):
                for index_y in range(3):
                    screen.blit(chunks[index_x + 3 * index_y], (camera_x + width * index_x, camera_y + height * index_y))
            screen.blit(hero.get_image(), (width // 2, height // 2))
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


    def show_menu():
        menu_background = load_image('background.jpg')
        start_button = Button(330, 60)
        quit_button = Button(135, 60)
        save_button = Button(400, 60)
        show = True

        while show:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            screen.blit(menu_background, (0, 0))
            start_button.draw(780, 340, 'START GAME', start_game)
            quit_button.draw(870, 565, 'QUIT', quit)
            save_button.draw(750, 450, 'UPLOAD A SAVE' )

            pygame.display.update()



    show_menu()


