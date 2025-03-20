# src/visualization/vis_components/resource_renderer.py
import pygame
import numpy as np  # Import numpy
from . import pole_sprite  # Import the pole_sprite module

RESOURCE_COLOR = (255, 255, 0)  # Yellow

def grid_to_iso(grid_x, grid_y, height, tile_width, tile_height):
    """Converts grid coordinates to isometric screen coordinates."""
    screen_x = (grid_x - grid_y) * tile_width / 2
    screen_y = (grid_x + grid_y) * tile_height / 2 - height
    return screen_x, screen_y

def draw_resources(screen, resource_map, terrain, position_manager, terrain_sprites, scale=1.0):
    resource_size = position_manager.get_resource_size() * scale  # Scale
    cell_size = position_manager.get_terrain_cell_size()
    tile_width = cell_size * 2 * scale  # Scale
    tile_height = cell_size * scale  # Scale

    # Define colors (as you requested)
    pole_color_profile = {
        "pole": (139, 69, 19),  # Brown
        "top": (255, 255, 0),  # Yellow
        "outline": (0, 0, 0)  # Black
    }

    for (x, y), amount in np.ndenumerate(resource_map):
        if amount > 0:  # If there's a resource at this location
            height_value = terrain[y, x] # Get the height directly from the terrain
            screen_x, screen_y = grid_to_iso(x, y, height_value, tile_width, tile_height)
            screen_x, screen_y = position_manager.get_render_position(screen_x, screen_y)

            # Calculate position
            resource_x = int(screen_x + tile_width / 2)  # Tile's center X
            resource_y = int(screen_y)  # screen_y already includes the height offset

            # --- Pole Sprite Implementation ---
            # Check if pole sprite exists with current tile_width and tile_height
            pole_key = (tile_width, tile_height)
            if pole_key not in pole_cache:
                #Create the pole sprite.
                pole_surface = pole_sprite.create_isometric_pole(int(tile_width), int(tile_height), pole_color_profile)
                pole_cache[pole_key] = pole_surface
            else:
                pole_surface = pole_cache[pole_key]

            # Blit the pole sprite onto the screen
            # Adjust the blit position to account for the pole's height and to center it
            blit_x = resource_x - pole_surface.get_width() // 2  # Center horizontally
            blit_y = resource_y - pole_surface.get_height()  # Align top of pole with top of tile

            screen.blit(pole_surface, (blit_x, blit_y))
            # --- End Pole Sprite Implementation ---
            
pole_cache = {} #Dictionary to store pole sprite to avoid recreating the pole sprite every frame