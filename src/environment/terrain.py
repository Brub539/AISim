import numpy as np
from noise import snoise2  # For Perlin noise
import math
import random
from scipy.ndimage import gaussian_filter  # Import Gaussian filter

# Define terrain colors
COLOR_SAND  = (245, 222, 179)
COLOR_GRASS = (124, 252, 0)
COLOR_STONE = (112, 128, 144)
COLOR_SNOW  = (255, 250, 250)
COLOR_WATER = (60, 60, 200)  # Water color

# Terrain types
TERRAIN_SAND   = 0
TERRAIN_GRASS  = 1
TERRAIN_STONE  = 2
TERRAIN_SNOW   = 3
TERRAIN_WATER  = 4

# ------------------------------------------------------------------
# Terrain Generation Parameters (NEW - as dictionary)
# ------------------------------------------------------------------
def create_scaled_params(width, height):
    """
    Returns a dictionary of terrain generation parameters.
    By default, these produce the same results as your
    current code when width=100 and height=100.
    """
    scale_factor_area = (width * height) / (width * height)
    # If you want linear scaling, you could also do:
    # scale_factor_linear = min(width, height) / 100.0

    return {
        "min_mountains": int(max(1, 7  * scale_factor_area)),
        "max_mountains": int(max(1, 20 * scale_factor_area)),

        "mountain_radius_factor": 0.5,    # 0.5  default from your code
        "mountain_height_divisor": 30.0,  # 30.0 default from your code
        "mountain_height_factor": 4.0,    # 4.0  default from your code

        "gaussian_sigma": 2.0,            # 2.0  default from your code
        "num_smoothing_iterations": 5,    # 5    default from your code
        "max_height_difference": 1.0,     # 1.0  default from your code
        "terrace_step": 1.0               # 1.0  default from your code
    }

def smooth_terrace(hmap, step=1.0):
    """
    Applies a smooth terracing function using a smoothstep.
    Instead of hard steps, it blends each step boundary for smoother transitions.
    """
    terraces = np.floor(hmap / step)
    fraction = (hmap / step) - terraces
    smoothed_fraction = fraction * fraction * (3 - 2 * fraction)
    return np.clip((terraces + smoothed_fraction) * step, 0.0, 1.0)

def blend_colors(color1, color2, blend_factor):
    """Blends two RGB colors based on a blend factor (0.0 to 1.0)."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 * (1 - blend_factor) + r2 * blend_factor)
    g = int(g1 * (1 - blend_factor) + g2 * blend_factor)
    b = int(b1 * (1 - blend_factor) + b2 * blend_factor)
    return (r, g, b)

# ------------------------------------------------------------------
# Main Heightmap Generation Function
# ------------------------------------------------------------------
def generate_heightmap(width, height, params=None):
    """
    Generates a heightmap with mountain overlay, Gaussian blur smoothing,
    and rivers that cut across the terrain, with smoothed edges.

    If 'params' is None, we use the default parameter dictionary
    returned by create_scaled_params(width, height).
    """
    if params is None:
        params = create_scaled_params(width, height)

    # Extract parameters for clarity
    min_mountains       = params["min_mountains"]
    max_mountains       = params["max_mountains"]
    radius_factor       = params["mountain_radius_factor"]
    height_divisor      = params["mountain_height_divisor"]
    height_factor       = params["mountain_height_factor"]
    sigma               = params["gaussian_sigma"]
    num_iterations      = params["num_smoothing_iterations"]
    max_height_diff     = params["max_height_difference"]
    terrace_step        = params["terrace_step"]

    # Initialize maps
    heightmap = np.zeros((height, width), dtype=np.float32)
    terrain_color_map = np.zeros((height, width, 3), dtype=np.uint8)
    terrain_type_map  = np.zeros((height, width), dtype=np.int32)

    # 1. Mountain Generation with Randomness
    num_mountains = random.randint(min_mountains, max_mountains)

    for _ in range(num_mountains):
        # Example relationship: radius is up to ~ half of the smaller dimension
        mountain_radius = int(random.randint(1, min(width, height)) * radius_factor)

        # Mountain height uses your 30:4 ratio by default
        mountain_height = (mountain_radius / height_divisor) * height_factor

        # Random center
        mountain_center = (
            random.randint(0, width - 1),
            random.randint(0, height - 1)
        )

        if mountain_center and mountain_radius > 0:
            center_x, center_y = mountain_center
            for y in range(height):
                for x in range(width):
                    dist = math.hypot(x - center_x, y - center_y)
                    if dist <= mountain_radius:
                        normalized_dist = dist / mountain_radius
                        height_addition = mountain_height * (1 - normalized_dist)

                        # Get the current height and neighbors
                        current_height = heightmap[y, x]
                        neighbors = [
                            (x-1, y), (x+1, y),
                            (x, y-1), (x, y+1)
                        ]
                        neighbor_heights = []
                        
                        for nx, ny in neighbors:
                            if 0 <= nx < width and 0 <= ny < height:
                                neighbor_heights.append(heightmap[ny, nx])
                        
                        if neighbor_heights:
                            # Calculate allowed min/max based on neighbors
                            max_allowed = max(neighbor_heights) + max_height_diff
                            min_allowed = min(neighbor_heights) - max_height_diff

                            # Constrain new height
                            new_height = current_height + height_addition
                            new_height = min(new_height, max_allowed)
                            new_height = max(new_height, min_allowed)

                            heightmap[y, x] = new_height

    # 2. Apply Gaussian Blur
    heightmap = gaussian_filter(heightmap, sigma=sigma)

    # 3. Post-Mountain Height Constraint
    for _ in range(num_iterations):
        for y in range(height):
            for x in range(width):
                # Broader neighbor search (include diagonals)
                neighbors = [
                    (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                    (x - 1, y - 1), (x + 1, y - 1),
                    (x - 1, y + 1), (x + 1, y + 1)
                ]
                for nx, ny in neighbors:
                    if 0 <= nx < width and 0 <= ny < height:
                        diff = heightmap[y, x] - heightmap[ny, nx]
                        if abs(diff) > max_height_diff:
                            if diff > 0:
                                heightmap[y, x] = heightmap[ny, nx] + max_height_diff
                            else:
                                heightmap[y, x] = heightmap[ny, nx] - max_height_diff

    # 4. Normalize heightmap to [0, 1]
    min_val = heightmap.min()
    max_val = heightmap.max()
    if max_val > min_val:
        heightmap = (heightmap - min_val) / (max_val - min_val)

    # 5. Apply smooth terracing
    heightmap = smooth_terrace(heightmap, step=terrace_step)

    # 6. (Optional) River Generation (commented out)
    # from .river_generation import add_rivers
    # add_rivers(heightmap, terrain_type_map)

    # 7. Assign terrain types & colors
    water_threshold = 0.2
    sand_threshold  = 0.3
    grass_threshold = 0.6
    stone_threshold = 0.75

    for y in range(height):
        for x in range(width):
            h = heightmap[y, x]
            if h < water_threshold:
                terrain_color_map[y, x] = COLOR_WATER
                terrain_type_map[y, x]  = TERRAIN_WATER
            elif h < sand_threshold:
                terrain_color_map[y, x] = COLOR_SAND
                terrain_type_map[y, x]  = TERRAIN_SAND
            elif h < grass_threshold:
                blend = (h - sand_threshold) / (grass_threshold - sand_threshold)
                terrain_color_map[y, x] = blend_colors(COLOR_SAND, COLOR_GRASS, blend)
                terrain_type_map[y, x]  = TERRAIN_GRASS
            elif h < stone_threshold:
                blend = (h - grass_threshold) / (stone_threshold - grass_threshold)
                terrain_color_map[y, x] = blend_colors(COLOR_GRASS, COLOR_STONE, blend)
                terrain_type_map[y, x]  = TERRAIN_STONE
            else:
                blend = (h - stone_threshold) / (1.0 - stone_threshold)
                terrain_color_map[y, x] = blend_colors(COLOR_STONE, COLOR_SNOW, blend)
                terrain_type_map[y, x]  = TERRAIN_SNOW

    return heightmap, terrain_color_map, terrain_type_map

# ------------------------------------------------------------------
# Supporting functions
# ------------------------------------------------------------------
def get_height(heightmap, x, y):
    x = int(x)
    y = int(y)
    if 0 <= x < heightmap.shape[1] and 0 <= y < heightmap.shape[0]:
        return heightmap[y, x]
    else:
        return 0

def get_terrain_color(terrain_color_map, x, y):
    x = int(x)
    y = int(y)
    if 0 <= x < terrain_color_map.shape[1] and 0 <= y < terrain_color_map.shape[0]:
        return terrain_color_map[y, x]
    else:
        return (0, 0, 0)

def get_terrain_type(terrain_type_map, x, y):
    x = int(x)
    y = int(y)
    if 0 <= x < terrain_type_map.shape[1] and 0 <= y < terrain_type_map.shape[0]:
        return terrain_type_map[y, x]
    else:
        return -1

def calculate_slope(heightmap, x, y, delta=1):
    x = int(x)
    y = int(y)
    if not (0 <= x < heightmap.shape[1] and 0 <= y < heightmap.shape[0]):
        return 0
    slopes = []
    for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < heightmap.shape[1] and 0 <= new_y < heightmap.shape[0]:
            height_diff = abs(heightmap[new_y, new_x] - heightmap[y, x])
            slopes.append(height_diff / delta)
    return max(slopes) if slopes else 0

def is_walkable(heightmap, x, y, terrain_type_map, max_slope=0.3):
    x = int(x)
    y = int(y)
    if not (0 <= x < heightmap.shape[1] and 0 <= y < heightmap.shape[0]):
        return False
    terrain_type = get_terrain_type(terrain_type_map, x, y)
    slope = calculate_slope(heightmap, x, y)
    if terrain_type == TERRAIN_SNOW:
        max_slope *= 0.5
    elif terrain_type == TERRAIN_STONE:
        max_slope *= 0.8
    return slope <= max_slope
