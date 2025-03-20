# src/agent/movement.py
import numpy as np
from src.environment.terrain import is_walkable, calculate_slope, get_terrain_type, TERRAIN_SAND, TERRAIN_GRASS, TERRAIN_STONE, TERRAIN_SNOW, TERRAIN_WATER # Import needed functions
from src.agent import vision  # Import vision module
import random

# Movement costs for each terrain type (adjusted for better survival)
TERRAIN_MOVEMENT_COST = {
    TERRAIN_SAND: 0.6,  # Sand is moderately challenging
    TERRAIN_GRASS: 0.3,  # Grass is easiest to traverse
    TERRAIN_STONE: 0.8,  # Stone is quite challenging
    TERRAIN_SNOW: 1.0,  # Snow is most difficult
}

# Speed multipliers for each terrain type
TERRAIN_SPEED_MULTIPLIER = {
    TERRAIN_SAND: 0.8,   # Slower in sand
    TERRAIN_GRASS: 1.2,  # Faster on grass
    TERRAIN_STONE: 0.7,  # Slower on stone
    TERRAIN_SNOW: 0.5,   # Slowest in snow
    4: 0.4,    # Very slow in water (using terrain type value 4 for water)
}

def move(agent, dx, dy, terrain, terrain_type_map, delta):
    """Moves the agent in a given direction, consuming energy and handling height differences."""
    # Apply base speed of 2 tiles per second
    base_speed = 4.0
    
    # Get current terrain type and apply speed multiplier
    current_terrain = get_terrain_type(terrain_type_map, round(agent.x), round(agent.y))
    speed_multiplier = TERRAIN_SPEED_MULTIPLIER.get(current_terrain, 1.0)
    
    # Store the speed multiplier in the agent for sidebar display
    agent.terrain_speed_multiplier = speed_multiplier
    
    # Apply speed multiplier to movement
    dx = dx * base_speed * speed_multiplier * delta
    dy = dy * base_speed * speed_multiplier * delta
    
    # Calculate grid-based movement
    new_x = agent.x + dx
    new_y = agent.y + dy

    # Convert to integers for indexing
    int_new_x = int(new_x)
    int_new_y = int(new_y)

    if 0 <= int_new_x < terrain.shape[1] and 0 <= int_new_y < terrain.shape[0]:
        # Get current and target heights
        current_height = terrain[int(agent.y), int(agent.x)]
        target_height = terrain[int_new_y, int_new_x]
        height_diff = abs(target_height - current_height)
        
        # Check if the height difference is walkable (max step height = 1 unit)
        if height_diff <= 1 and is_walkable(terrain, int_new_x, int_new_y, terrain_type_map):
            energy_cost = calculate_energy_cost(terrain, agent.x, agent.y, new_x, new_y, terrain_type_map)  # Using new parameters
            if agent.energy >= energy_cost:
                # Update position with the calculated speed
                agent.x = new_x
                agent.y = new_y
                agent.energy -= energy_cost
                return True  # Moved successfully
            else:
                return False  # Not enough energy
        else:
            return False  # Invalid move

def calculate_energy_cost(terrain, x1, y1, x2, y2, terrain_type_map):
    """Calculates the energy cost of moving between two points, considering terrain type."""
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    slope = calculate_slope(terrain, x1, y1)  # Assuming slope affects energy cost
    
    # Get the terrain type at the starting position
    terrain_type = get_terrain_type(terrain_type_map, x1, y1)
    
    # Get the movement cost multiplier for the terrain type
    terrain_multiplier = TERRAIN_MOVEMENT_COST.get(terrain_type, 1.0)  # Default to 1.0 if not found

    # Adjusted formula: base cost is lower, slope has less impact
    base_cost = 0.2  # Reduced base energy cost
    slope_factor = 0.5 * slope  # Reduced slope impact
    energy_cost = distance * terrain_multiplier * (base_cost + slope_factor)
    return energy_cost

def move_towards_resource(agent, terrain, terrain_type_map, resource_map, delta):
    """Finds the nearest resource and moves the agent towards it."""
    # Find the nearest resource (very basic implementation)
    nearest_resource = vision.find_nearest_resource(agent, resource_map, terrain)
    if nearest_resource:
        rx, ry = nearest_resource
        # Check if it is target_resource.
        if agent.target_resource == (rx, ry):
            agent.attempts_to_reach += 1
            if agent.attempts_to_reach > agent.max_attempts:
                # If its above, the resource is considered non accesible. The bot needs to drop the resource and find another one.
                agent.target_resource = None
                agent.attempts_to_reach = 0
                return resource_map  # Return immediately.
        # Found a new resource, make it a target
        else:
            agent.target_resource = (rx, ry)
            agent.attempts_to_reach = 0

        dx = 0
        dy = 0

        if rx > agent.x:
            dx = 1
        elif rx < agent.x:
            dx = -1

        if ry > agent.y:
            dy = 1
        elif ry < agent.y:
            dy = -1

        # Try to move towards the resource
        if not move(agent, dx, dy, terrain, terrain_type_map, delta): #Send the parameters.
            # If the move fails, try a random move.
            dx = np.random.choice([-1, 0, 1])
            dy = np.random.choice([-1, 0, 1])
            move(agent, dx, dy, terrain, terrain_type_map, delta) #Send the parameters.

        # Try to collect if nearby
        if abs(agent.x - rx) <= 1 and abs(agent.y - ry) <= 1:  # Simple proximity check
            resource_map = vision.collect_resource(agent, resource_map, rx, ry)  # Collect the resource.
            agent.target_resource = None  # Unset the resource.
            agent.attempts_to_reach = 0  # Reset the action as well.

    else:
        # No resources found, move randomly.
        dx = np.random.choice([-1, 0, 1])
        dy = np.random.choice([-1, 0, 1])
        move(agent, dx, dy, terrain, terrain_type_map, delta) #Send the parameters.

    return resource_map