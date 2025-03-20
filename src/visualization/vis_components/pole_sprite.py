# src/visualization/vis_components/pole_sprite.py
import pygame

def create_isometric_pole(tile_width, tile_height, color_profile, pole_height_factor=2):
    """
    Generates an isometric pole sprite that appears to stand on a tile.

    Args:
        tile_width (int): The width of the tile (horizontal dimension).
        tile_height (int): The *maximum* height of the tile (vertical dimension).
        color_profile (dict): Dictionary containing colors for different parts of the pole.
        pole_height_factor (float): How many times higher than the tile should the pole be.

    Returns:
        pygame.Surface: A Pygame surface containing the rendered isometric pole.
    """

    pole_height = int(tile_height * pole_height_factor)
    pole_surface = pygame.Surface((tile_width, pole_height + tile_height // 2), pygame.SRCALPHA)  # Add extra space for the top
    pole_surface = pole_surface.convert_alpha()

    # Define the pole's dimensions
    pole_width = tile_width // 4  # Pole width is 1/4 of the tile width
    pole_x_offset = (tile_width - pole_width) // 2  # Center the pole horizontally

    # Calculate the starting points for the pole
    x1 = tile_width // 2  # Center X
    y1 = tile_height // 3 # Height of the tile top
    x2 = x1 - pole_width // 2
    y2 = y1 + tile_height // 6
    x3 = x1 + pole_width // 2
    y3 = y1 + tile_height // 6
    x4 = x1
    y4 = tile_height // 3 + pole_height

    # Draw the pole's main body (a trapezoid)
    pole_points = [(x2,y2),(x3,y3),(x4,y4),(x1, y1 + pole_height - tile_height // 6)]
    pygame.draw.polygon(pole_surface, color_profile["pole"], pole_points)

    # Draw outline
    pygame.draw.line(pole_surface, color_profile["outline"], pole_points[0], pole_points[1], 1)
    pygame.draw.line(pole_surface, color_profile["outline"], pole_points[1], pole_points[2], 1)
    pygame.draw.line(pole_surface, color_profile["outline"], pole_points[2], pole_points[3], 1)
    pygame.draw.line(pole_surface, color_profile["outline"], pole_points[3], pole_points[0], 1)

    # Draw a simple "top" for the pole (a circle)
    pygame.draw.circle(pole_surface, color_profile["top"], (tile_width // 2, tile_height//3 + pole_height), tile_width // 8)
    pygame.draw.circle(pole_surface, color_profile["outline"], (tile_width // 2, tile_height//3 + pole_height), tile_width // 8, 1)

    return pole_surface

if __name__ == '__main__':
    # Example Usage
    pygame.init()
    screen_width = 400
    screen_height = 300
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Isometric Pole Test")

    # Define colors
    pole_color_profile = {
        "pole": (139, 69, 19),  # Brown
        "top": (255, 255, 0),  # Yellow
        "outline": (0, 0, 0)  # Black
    }

    # Create the isometric pole sprite
    tile_width = 40
    tile_height = 40
    pole_sprite = create_isometric_pole(tile_width, tile_height, pole_color_profile)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 100, 200))  # Sky color background

        # Blit the pole onto the screen
        screen.blit(pole_sprite, (100, 50))

        pygame.display.flip()

    pygame.quit()