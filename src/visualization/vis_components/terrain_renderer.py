# src/visualization/vis_components/terrain_renderer.py
import pygame
from src.visualization.vis_components import cube_sprite
import numpy as np  # Import numpy

# Extract the constants that are specifically used by this module.
TILE_WIDTH = 40   # Adjust for desired tile size
TILE_HEIGHT = 40  # Total height of the cube

# Define color for each type, now including water (type 4)
TERRAIN_COLORS = {
    0: {  # Sand color
        "top": (214, 198, 148),
        "left": (174, 158, 108),
        "right": (194, 178, 128),
        "outline": (100, 84, 34)
    },
    1: {  # Grass color
        "top": (20, 148, 20),
        "left": (0, 108, 0),
        "right": (0, 128, 0),
        "outline": (0, 48, 0)
    },
    2: {  # Stone color
        "top": (148, 148, 148),
        "left": (108, 108, 108),
        "right": (128, 128, 128),
        "outline": (48, 48, 48)
    },
    3: {  # Snow color
        "top": (255, 255, 255),
        "left": (200, 200, 200),
        "right": (230, 230, 230),
        "outline": (150, 150, 150)
    },
    4: {  # Water color
        "top": (60, 60, 200),    # Lighter blue on top
        "left": (40, 40, 140),   # Darker on the left face
        "right": (50, 50, 180),  # Medium blue on the right face
        "outline": (20, 20, 50)  # Dark outline
    }
}

def create_terrain_sprites(tile_width, tile_height):
    """Generates and returns a dictionary of pre-rendered terrain sprites."""
    terrain_sprites = {}
    for terrain_type, color_profile in TERRAIN_COLORS.items():
        # Pixelate the colors before passing them to create_isometric_cube
        pixelated_color_profile = {
            k: cube_sprite.pixelate_color(v) for k, v in color_profile.items()
        }
        terrain_sprites[terrain_type] = cube_sprite.create_isometric_cube(
            tile_width, tile_height, pixelated_color_profile
        )
    return terrain_sprites

def grid_to_iso(grid_x, grid_y, height, tile_width, tile_height):
    """Converts grid coordinates to isometric screen coordinates."""
    screen_x = (grid_x - grid_y) * tile_width / 2
    screen_y = (grid_x + grid_y) * tile_height / 2 - height
    return screen_x, screen_y

def draw_terrain(screen, terrain, terrain_type_map, position_manager, terrain_sprites, constrained_heights, scale=1.0):
    """Draws the terrain with subpixel positioning."""
    height, width = terrain.shape
    cell_size = position_manager.get_terrain_cell_size()
    tile_width = cell_size * 2 * scale
    tile_height = cell_size * scale

    for y in range(height):
        for x in range(width):
            # Use the pre-calculated constrained height
            screen_x, screen_y = grid_to_iso(x, y, constrained_heights[y, x] * scale, tile_width, tile_height)
            screen_x, screen_y = position_manager.get_render_position(screen_x, screen_y)

            # Get the terrain type and corresponding sprite
            terrain_type = int(terrain_type_map[y, x].item())  # Ensure it's an integer
            sprite = terrain_sprites[terrain_type]

            # Blit the sprite onto the screen using floating-point coordinates and then rounding
            screen.blit(sprite, (round(screen_x), round(screen_y)))