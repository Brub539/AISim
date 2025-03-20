# src/main.py
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pygame
import random

from environment import terrain, resource
from agent import agent
from visualization import primer_vis  # Now Pygame visualization

# Import our water update and river-adding functions
from environment.river_generation import update_water, add_rivers

def calculate_constrained_heights(terrain, tile_height):
    """Calculates and returns a 2D array of constrained tile heights."""
    height, width = terrain.shape
    constrained_heights = np.zeros_like(terrain, dtype=np.float32)
    max_height_diff = tile_height

    for y in range(height):
        for x in range(width):
            height_value = terrain[y, x] * 1  # Scale factor

            # Enforce Height Constraints
            constrained_height = height_value
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            # Calculate scaling factor based on map width (assuming a square map):
            # Using the quadratic: factor = (1/300)*width^2 + (67/15)*width + 20
            scale_factor = (width**2) / 300.0 + (67.0 / 15.0) * width + 20.0
            for nx, ny in neighbors:
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_height_value = terrain[ny, nx] * scale_factor  # Scale the raw heightmap value
                    diff = constrained_height - neighbor_height_value
                    if diff > max_height_diff:
                        constrained_height = neighbor_height_value + max_height_diff
                    elif diff < -max_height_diff:
                        constrained_height = neighbor_height_value - max_height_diff

            constrained_heights[y, x] = constrained_height


    return constrained_heights

def main():
    """Main simulation loop."""
    # --- Simulation Parameters ---
    mapconfig = 30
    width = mapconfig
    height = mapconfig
    num_resources = 25  # Increased from 15 to match larger map
    num_agents = 3

    # --- Configuration ---
    config = {
        'simulation_speed': 0.1,
        'food_respawn_interval': 3000,
        'aging_interval': 5000
    }

    # --- Initialize Environment ---
     # Generate a heightmap with a grass baseline and Perlin noise
    _terrain, _terrain_color_map, _terrain_type_map = terrain.generate_heightmap(
        width=width,
        height=height,
    )

    resource_map, resource_locations = resource.distribute_resources(_terrain, _terrain_type_map, num_resources)

    # Pre-render terrain sprites
    terrain_sprites = primer_vis.terrain_renderer.create_terrain_sprites(
        primer_vis.terrain_renderer.TILE_WIDTH, primer_vis.terrain_renderer.TILE_HEIGHT
    )

    # --- Calculate Constrained Heights (ONCE) ---
    constrained_heights = calculate_constrained_heights(_terrain, primer_vis.terrain_renderer.TILE_HEIGHT)

    # --- Initialize Water Simulation Data ---
    water_flow = np.zeros((_terrain.shape[0], _terrain.shape[1], 2), dtype=np.float32)
    water_dryness = np.zeros((_terrain.shape[0], _terrain.shape[1]), dtype=np.float32)
    diffusion_rate = 0.1  # Rate at which water spreads
    momentum = 0.5  # How much water retains its previous direction
    water_update_interval = 5.0  # seconds
    last_water_update = pygame.time.get_ticks()  # in milliseconds
    dryness_threshold = 5.0  # seconds before isolated water dries
    erosion_rate = 0.0005   # How quickly terrain erodes under water

    # --- Initialize Agents ---
    agents = []
    num_groups = 2
    group_letters = [chr(i) for i in range(ord('A'), ord('A') + num_groups)]
    group_colors = {}

    for i in range(num_agents):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        group_id = random.randint(0, num_groups - 1)

        if group_id not in group_colors:
            group_colors[group_id] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )

        new_agent = agent.Agent(x=x, y=y, group=group_id)
        new_agent.color = group_colors[group_id]
        agents.append(new_agent)

    for ag in agents:
        ag.age = 0

    # --- Simulation Loop ---
    running = True
    last_food_respawn = pygame.time.get_ticks()
    last_aging = pygame.time.get_ticks()

    # Create a Clock object for managing frame rate.
    clock = pygame.time.Clock()

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds, capped at 60 FPS.

        # Process events. If a quit event is detected, break immediately.
        if primer_vis.handle_events(config, dt):
            break

        # --- Water Simulation Update (every 5 seconds) ---
        current_time = pygame.time.get_ticks()
        if current_time - last_water_update >= water_update_interval * 1000:
            update_water(
                _terrain,
                _terrain_type_map,
                water_flow,
                water_dryness,
                dt,
                dryness_threshold=dryness_threshold,
                erosion_rate=erosion_rate,
                diffusion_rate=diffusion_rate,  # Add diffusion rate
                momentum=momentum               # Add momentum
            )
            last_water_update = current_time

        # Update Agents and Environment
        # Base speed of 2 tiles per second, properly scaled with simulation speed
        delta = dt * config['simulation_speed']  # Remove the 2.0 multiplier since it's handled in movement.py
        for ag in agents:
            if ag.is_alive():
                # Pass water_flow so water affects movement.
                resource_map = ag.update(
                    _terrain,
                    _terrain_type_map,
                    resource_map,
                    delta,
                    water_flow=water_flow
                )

        # Delayed food respawn logic
        current_time = pygame.time.get_ticks()
        if current_time - last_food_respawn >= config['food_respawn_interval'] / config['simulation_speed']:
            resource_map, resource_locations = resource.respawn_resources(_terrain, _terrain_type_map, num_resources)
            last_food_respawn = current_time

        # Update age every X seconds.
        if current_time - last_aging >= config["aging_interval"]:
            for ag in agents:
                if ag.is_alive():
                    ag.age += 1
                    ag.max_energy = ag.calculate_max_energy()
                    ag.adjust_energy_level()
            last_aging = current_time

        # Update Pygame Display.
        primer_vis.update_display(
            _terrain,
            _terrain_type_map,
            resource_map,
            agents,
            config,
            group_letters,
            terrain_sprites,
            constrained_heights #Pass the constrained heights value.
        )

    primer_vis.close()  # Close pygame when finished.

if __name__ == "__main__":
    main()