from pynoise.noisemodule import Billow, Clamp
from pynoise.noiseutil import noise_map_plane_gpu
from pynoise.noiseutil import RenderImage
from pynoise.noiseutil import GradientColor
from pynoise.colors import Color

from sprites import Tile

tile_width = tile_height = 96


class World:
    def __init__(self, chunks_group_of_sprites, width, height, seed, screen_width, screen_height):
        self.chunks_group_of_sprites = chunks_group_of_sprites
        self.width = width
        self.height = height
        self.seed = seed  # от -119599999999999999 до 179499999845941242
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.array_of_tiles = []
        self.world_line = None
        self.world_grid = []
        self.main_chunk_x = None
        self.main_chunk_y = None

    def create_world(self):
        sourse = Clamp(Billow(seed=self.seed), -1, 0)
        self.world_line = noise_map_plane_gpu(width=self.width, height=self.height, lower_x=2,
                                              upper_x=6, lower_z=1, upper_z=5, source=sourse)
        chunk_size_x = self.screen_width // tile_width
        chunk_size_y = self.screen_height // tile_height
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
                        spawn_x = x % chunk_size_x * tile_width
                        spawn_y = (self.height - y) % chunk_size_y * tile_height
                        break
            self.world_grid.append(line_x)
        self.world_grid = self.world_grid[::-1]
        self.world_grid[spawn_y // tile_height + self.main_chunk_y * chunk_size_y][spawn_x // tile_width + self.main_chunk_x * chunk_size_x] = 1
        return spawn_x, spawn_y

    def draw(self, direction=None):
        tile_type = None
        chunk_size_x = self.screen_width // tile_width
        chunk_size_y = self.screen_height // tile_height
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

        start_index_x = -1
        index_y = -1
        if direction == "up":
            final_y = start_y
            final_y += 1
        if direction == "down":
            start_y = final_y
            start_y -= 1
            index_y = 1
        if direction == "right":
            start_x = final_x
            start_x -= 1
            start_index_x = 1
        if direction == "left":
            final_x = start_x
            final_x += 1

        for chunk_y in range(start_y, final_y):
            index_y += 1
            index_x = start_index_x
            for chunk_x in range(start_x, final_x):
                index_x += 1
                for y in range(chunk_size_y):
                    for x in range(chunk_size_x):
                        tile_num = self.world_grid[chunk_y * chunk_size_y + y][chunk_x * chunk_size_x + x]
                        if -1 <= tile_num < -0.2:
                            tile_type = "water.png"
                        if -0.2 <= tile_num < 0:
                            tile_type = "sand0.png"
                        if tile_num == 0:
                            tile_type = "grass.png"
                        if tile_num == 1:
                            tile_type = "pers.png"
                        Tile(self.chunks_group_of_sprites[index_x + index_y * 3], tile_type, x, y)

    def make_map(self):
        gradient = GradientColor()
        gradient.add_gradient_point(-1, Color(0, 0, 0.5))
        gradient.add_gradient_point(-0.2, Color(0.75, 0.75, 0.5))
        gradient.add_gradient_point(0, Color(0, 0.75, 0))
        gradient.add_gradient_point(1, Color(0.5, 0.75, 1))
        render = RenderImage()
        render.render(self.width, self.height, self.world_line, 'map.png', gradient)

    def update(self, chunks_group_of_sprites, direction):
        self.chunks_group_of_sprites = chunks_group_of_sprites
        if direction == "up":
            self.main_chunk_y -= 1
        if direction == "down":
            self.main_chunk_y += 1
        if direction == "right":
            self.main_chunk_x += 1
        if direction == "left":
            self.main_chunk_x -= 1
        self.draw(direction)
