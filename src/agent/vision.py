# src/agent/vision.py
import numpy as np
import pygame  # ADD THIS LINE
from src.environment.resource import get_resource_amount, deplete_resource

def find_nearest_resource(agent, resource_map, terrain):
    """Finds the nearest visible resource within 15 tiles, considering height limitations."""
    min_distance = float('inf')
    nearest_resource = None
    resource_locations = np.argwhere(resource_map > 0)  # Get coordinates where resource > 0
    agent_height = terrain[int(agent.y), int(agent.x)]

    for y, x in resource_locations:  # Note the y,x order is important here.
        distance = np.sqrt((agent.x - x)**2 + (agent.y - y)**2)
        if distance <= 15:  # Only check resources within 15 tiles
            target_height = terrain[y, x]
            # Agent can see resources at its height or below
            if target_height <= agent_height:
                if distance < min_distance:
                    min_distance = distance
                    nearest_resource = (x, y)

    return nearest_resource

def collect_resource(agent, resource_map, x, y):
    """Collects a resource, gaining energy."""
    x = int(x)
    y = int(y)
    resource_amount = get_resource_amount(resource_map, x, y)
    if resource_amount > 0:
        resource_map = deplete_resource(resource_map, x, y)  # Update resource map
        # Provide more energy gain for younger agents to help them survive
        age_factor = max(0.5, 1.0 - (agent.age / agent.max_age))  # Higher multiplier for younger agents
        agent.energy += resource_amount * 75 * age_factor  # Increased base energy gain with age scaling
        agent.last_ate = pygame.time.get_ticks()  # Update last ate time

        #Ensure is never over the max
        agent.energy = min(agent.energy, agent.max_energy)
        agent.last_eat_update = pygame.time.get_ticks()

    return resource_map  # Return updated resource map