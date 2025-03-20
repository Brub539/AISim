# src/environment/resource.py
import numpy as np
import random
from src.environment.terrain import generate_heightmap, is_walkable, get_terrain_type, TERRAIN_GRASS, TERRAIN_SAND, TERRAIN_STONE, TERRAIN_SNOW  # Import needed functions

# Resource growth rates for each terrain type (adjust as needed)
RESOURCE_GROWTH_RATES = {
    TERRAIN_SAND: 0.1,
    TERRAIN_GRASS: 0.5,
    TERRAIN_STONE: 0.05,
    TERRAIN_SNOW: 0.01,
}

def distribute_resources(terrain, terrain_type_map, num_resources, resource_type="food"):
    """Distributes resources randomly on the terrain, influenced by terrain type."""
    height, width = terrain.shape
    resource_map = np.zeros((height, width))
    resource_locations = []

    for _ in range(num_resources):
        # Find a random location
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        # Ensure that location is walkable and adjust probability based on terrain type
        while not is_walkable(terrain, x, y, terrain_type_map):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

        # Get terrain type
        terrain_type = get_terrain_type(terrain_type_map, x, y)

        #Place the resource
        resource_map[y, x] = 1  # Resource present
        resource_locations.append((x, y))

    return resource_map, resource_locations  # Return map and locations for other uses

def deplete_resource(resource_map, x, y, amount=1):
    """Depletes a resource at a given (x, y) coordinate."""
    if 0 <= x < resource_map.shape[1] and 0 <= y < resource_map.shape[0]:
        resource_map[y, x] = max(0, resource_map[y, x] - amount)  # Ensure resource doesn't go negative
    return resource_map

def regenerate_resource(resource_map, terrain, terrain_type_map, x, y, rate=0.1):
    """Regenerates a resource at a given (x, y) coordinate (influenced by sunlight and terrain type)."""
    if 0 <= x < resource_map.shape[1] and 0 <= y < resource_map.shape[0]:
        terrain_type = get_terrain_type(terrain_type_map, x, y)
        regeneration_rate = RESOURCE_GROWTH_RATES.get(terrain_type, 0.1)  # Default rate if terrain type not found

        # Placeholder for sunlight influence - replace with actual calculation later
        sunlight_factor = 1.0  # Replace with sunlight calculation

        resource_map[y, x] = min(1, resource_map[y, x] + regeneration_rate * sunlight_factor)  # Resource cap at 1

    return resource_map

def get_resource_amount(resource_map, x, y):
    """Returns the amount of resource at a given (x, y) coordinate."""
    if 0 <= x < resource_map.shape[1] and 0 <= y < resource_map.shape[0]:
        return resource_map[y, x]
    else:
        return 0

def respawn_resources(terrain, terrain_type_map, num_resources):
    """Respawns resources randomly on the terrain."""
    height, width = terrain.shape
    resource_map = np.zeros((height, width))
    resource_locations = []

    for _ in range(num_resources):
        # Find a random location
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        # Ensure that location is walkable
        while not is_walkable(terrain, x, y, terrain_type_map):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

        # Place the resource
        resource_map[y, x] = 1  # Resource present
        resource_locations.append((x, y))

    return resource_map, resource_locations  # Return map and locations for other uses


if __name__ == '__main__':
    # Example usage
    width = 20
    height = 20
    from src.environment.terrain import generate_heightmap  # Import it here as well

    terrain, terrain_type_map = generate_heightmap(width, height)
    num_resources = 10
    resource_map, resource_locations = distribute_resources(terrain, terrain_type_map, num_resources)

    print("Resource Map:\n", resource_map)
    print("Resource Locations:\n", resource_locations)