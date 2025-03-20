# src/visualization/vis_components/cube_sprite.py
import pygame

def create_isometric_cube(tile_width, tile_height, color_profile, height=None):
    """
    Generates an isometric cube sprite with a pixelated style and variable height.

    Args:
        tile_width (int): The width of the tile (horizontal dimension).
        tile_height (int): The *maximum* height of the tile (vertical dimension).
        color_profile (dict): Dictionary containing colors for different parts of the cube.
        height (int, optional): The actual height of the cube, must be lower than the max tile_height

    Returns:
        pygame.Surface: A Pygame surface containing the rendered isometric cube.
    """
    if height is None:
        height = tile_height # Use max height if no height is passed.
    
    height = min(height, tile_height) # height has to lower than the tile_height
    
    cube_surface = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)  # Use SRCALPHA for transparency
    cube_surface = cube_surface.convert_alpha()  # Ensure alpha channel works correctly

    # Calculate key points based on the *actual* tile height
    top_height = tile_height // 3  # Adjust this to control the height of the top face
    side_height = height - top_height

    top_points = [
        (tile_width // 2, 0),
        (tile_width, top_height // 2),
        (tile_width // 2, top_height),
        (0, top_height // 2)
    ]

    left_points = [
        (0, top_height // 2),
        (tile_width // 2, top_height),
        (tile_width // 2, height),  # Use variable height
        (0, side_height + top_height // 2)
    ]

    right_points = [
        (tile_width // 2, top_height),
        (tile_width, top_height // 2),
        (tile_width, side_height + top_height // 2),
        (tile_width // 2, height) # Use variable height
    ]

    # Draw the filled polygons for each face with the specified colors
    pygame.draw.polygon(cube_surface, color_profile["top"], top_points)
    pygame.draw.polygon(cube_surface, color_profile["left"], left_points)
    pygame.draw.polygon(cube_surface, color_profile["right"], right_points)

    # Draw the outline of the cube (Draw each line separately)
    pygame.draw.line(cube_surface, color_profile["outline"], top_points[0], top_points[1], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], top_points[1], top_points[2], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], top_points[2], top_points[3], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], top_points[3], top_points[0], 1)

    pygame.draw.line(cube_surface, color_profile["outline"], left_points[0], left_points[1], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], left_points[1], left_points[2], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], left_points[2], left_points[3], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], left_points[3], left_points[0], 1)

    pygame.draw.line(cube_surface, color_profile["outline"], right_points[0], right_points[1], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], right_points[1], right_points[2], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], right_points[2], right_points[3], 1)
    pygame.draw.line(cube_surface, color_profile["outline"], right_points[3], right_points[0], 1)

    return cube_surface

def pixelate_color(color):
    """Reduces the number of shades in a color by rounding RGB components."""
    r, g, b = color
    r = (r // 64) * 64  # Increased divisor to 64 for even more pixelation
    g = (g // 64) * 64
    b = (b // 64) * 64
    return (r, g, b)

if __name__ == '__main__':
    # Example Usage
    pygame.init()
    screen_width = 400
    screen_height = 300
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Isometric Cube Test")

    # Define colors (pre-pixelated)
    sand_color_profile = {
        "top": pixelate_color((214, 198, 148)),
        "left": pixelate_color((174, 158, 108)),
        "right": pixelate_color((194, 178, 128)),
        "outline": pixelate_color((100, 84, 34))
    }

    grass_color_profile = {
        "top": pixelate_color((20, 148, 20)),
        "left": pixelate_color((0, 108, 0)),
        "right": pixelate_color((0, 128, 0)),
        "outline": pixelate_color((0, 48, 0))
    }

    stone_color_profile = {
        "top": pixelate_color((148, 148, 148)),
        "left": pixelate_color((108, 108, 108)),
        "right": pixelate_color((128, 128, 128)),
        "outline": pixelate_color((48, 48, 48))
    }

    snow_color_profile = {
        "top": pixelate_color((255, 255, 255)),
        "left": pixelate_color((200, 200, 200)),
        "right": pixelate_color((230, 230, 230)),
        "outline": pixelate_color((150, 150, 150))
    }
    
    water_color_profile = {
        "top": pixelate_color((60, 60, 200)),    # Lighter top
        "left": pixelate_color((40, 40, 140)),   # Darker left face
        "right": pixelate_color((50, 50, 180)),  # Medium right face
        "outline": pixelate_color((20, 20, 50))  # Dark outline
    }

    # Create the isometric cube sprite
    tile_width = 40
    tile_height = 40  # Increased tile_height to create taller cubes

    sand_cube = create_isometric_cube(tile_width, tile_height, sand_color_profile)
    grass_cube = create_isometric_cube(tile_width, tile_height, grass_color_profile)
    stone_cube = create_isometric_cube(tile_width, tile_height, stone_color_profile)
    snow_cube = create_isometric_cube(tile_width, tile_height, snow_color_profile)
    water_cube = create_isometric_cube(tile_width, tile_height, water_color_profile)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 100, 200))  # Sky color background

        # Blit the cube onto the screen
        screen.blit(sand_cube, (50, 50))
        screen.blit(grass_cube, (150, 50))
        screen.blit(stone_cube, (250, 50))
        screen.blit(snow_cube, (350, 50))
        screen.blit(water_cube, (450, 50))

        pygame.display.flip()

    pygame.quit()