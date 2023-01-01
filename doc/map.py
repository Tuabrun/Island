from pynoise.noisemodule import Billow, Clamp
from pynoise.noiseutil import noise_map_plane_gpu
from pynoise.noiseutil import RenderImage
from pynoise.noiseutil import GradientColor
from pynoise.colors import Color

from random import randint

from sprites import Tile


def sprite_rotation(tile_num):
    turn = None
    tile_type = None
    if -1 <= tile_num < -0.2:
        tile_type = "water.png"
    if -0.2 <= tile_num < 0:
        num = randint(1, 100)
        if 1 <= num <= 15:
            tile_type = "sand1.png"
        if 16 <= num <= 30:
            tile_type = "sand2.png"
        if 31 <= num <= 100:
            tile_type = "sand0.png"
    if tile_num == 0:
        tile_type = "grass.png"
    if tile_num == 1:
        tile_type = "pers.png"
    tile_inf = (tile_type, turn)
    return tile_inf


class World:
    def __init__(self, tiles_group, all_sprites, width, height, seed):
        self.tiles_group = tiles_group
        self.all_sprites = all_sprites
        self.width = width
        self.height = height
        self.seed = seed  # от -119599999999999999 до 179499999845941242
        self.world_line = None
        self.world_grid = []
        self.main_chunk_x = None
        self.main_chunk_y = None

    def create_world(self, screen_width, screen_height):
        sourse = Clamp(Billow(seed=self.seed), -1, 0)
        self.world_line = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=2,
                                              upper_x=6, lower_z=1, upper_z=5, source=sourse)
        chunk_size_x = screen_width // 32
        chunk_size_y = screen_height // 32
        spawn_x = None
        spawn_y = None
        max_forest = 0

        for y in range(self.height):
            line_x = self.world_line[y * self.width:(y + 1) * self.width]

            number_of_forest = 0
            for tile_num in line_x:
                if tile_num == 0:
                    number_of_forest += 1
            if number_of_forest > max_forest:
                max_forest = number_of_forest
                for x in range(self.width):
                    if line_x[x] == 0 and (-0.2 <= line_x[x - 1] < 0 or -0.2 <= line_x[x - 1] < 0):
                        self.main_chunk_x = x // chunk_size_x
                        self.main_chunk_y = (self.height - y) // chunk_size_y
                        spawn_x = x % chunk_size_x * 32
                        spawn_y = (self.height - y) % chunk_size_y * 32
                        break
            self.world_grid.append(line_x)
        self.world_grid = self.world_grid[::-1]
        self.world_grid[spawn_y // 32 + self.main_chunk_y * chunk_size_y][spawn_x // 32 + self.main_chunk_x * chunk_size_x] = 1
        return spawn_x, spawn_y

    def draw(self, screen_width, screen_height):
        chunk_size_x = screen_width // 32
        chunk_size_y = screen_height // 32
        start_x = self.main_chunk_x
        start_y = self.main_chunk_y
        if start_x > 0:
            start_x -= 1
        if start_y > 0:
            start_y -= 1

        final_x = self.width // chunk_size_x
        final_y = self.height // chunk_size_y
        if final_x > 3:
            final_x = start_x + 3
        if final_y > 3:
            final_y = start_y + 3

        for chunk_y in range(start_y, final_y):
            for chunk_x in range(start_x, final_x):
                for y in range(chunk_size_y):
                    for x in range(chunk_size_x):
                        tile_num = self.world_grid[chunk_y * chunk_size_y + y][chunk_x * chunk_size_x + x]
                        tile_type, tile_turn = sprite_rotation(tile_num)
                        pos_x = chunk_size_x * (chunk_x - start_x) + x
                        pos_y = chunk_size_y * (chunk_y - start_y) + y
                        Tile(self.tiles_group, self.all_sprites, tile_type, pos_x, pos_y, tile_turn)
        x = chunk_size_x * (final_x - start_x) * 32
        y = chunk_size_y * (final_y - start_y) * 32
        return x, y

    def make_map(self):
        gradient = GradientColor()
        gradient.add_gradient_point(-1, Color(0, 0, 0.5))
        gradient.add_gradient_point(-0.2, Color(0.75, 0.75, 0.5))
        gradient.add_gradient_point(0, Color(0, 0.75, 0))
        gradient.add_gradient_point(1, Color(0.5, 0.75, 1))
        render = RenderImage()
        render.render(self.width, self.height, self.world_line, 'map.png', gradient)

    def update(self):
