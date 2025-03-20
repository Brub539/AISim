# src/visualization/primer_vis.py
import sys  # Import sys to call sys.exit()
import pygame
from typing import Optional
from src.environment import terrain as t, resource as r
from src.visualization.vis_components import terrain_renderer, resource_renderer, agent_renderer, sidebar
from src.visualization.vis_components.zoom import ZoomManager
import src.main as main

# --- Constants ---
SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 900
SIDEBAR_WIDTH = 430
GAME_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evolving Agents Simulation")
font = pygame.font.Font(None, 24)

# We will create the position manager later, so we initialize it as None.
from src.visualization.vis_components.position_manager import PositionManager
position_manager: Optional[PositionManager] = None

# Initialize Zoom Manager
zoom_manager = ZoomManager(initial_scale=1.0)

def update_display(terrain, terrain_type_map, resource_map, agents, config, group_letters, terrain_sprites, constrained_heights):
    global position_manager
    # If position_manager is not initialized, do it now using terrain dimensions.
    if position_manager is None:
        map_height, map_width = terrain.shape
        position_manager = PositionManager(
            game_width=GAME_WIDTH,
            screen_height=SCREEN_HEIGHT,
            map_width=map_width,
            map_height=map_height
        )
    
    screen.fill((0, 100, 200))  # Sky color background

    # Sync the position manager's zoom with the zoom manager.
    scale = zoom_manager.get_scale()
    position_manager.set_zoom(scale)

    # Create a surface that matches the game area size.
    game_surface = pygame.Surface((GAME_WIDTH, SCREEN_HEIGHT))

    # Draw terrain, resources, and agents directly onto game_surface.
    terrain_renderer.draw_terrain(
        game_surface, terrain, terrain_type_map, position_manager, terrain_sprites, constrained_heights, scale=1.0
    )
    resource_renderer.draw_resources(
        game_surface, resource_map, terrain, position_manager, terrain_sprites, scale=1.0
    )
    agent_renderer.draw_agents(
        game_surface, agents, terrain, position_manager, terrain_sprites, scale=1.0
    )

    # Blit the game_surface at (0, 0) in the main screen.
    screen.blit(game_surface, (0, 0))

    # Draw sidebar.
    sidebar.draw_sidebar(
        screen, agents, font, config,
        GAME_WIDTH, SCREEN_HEIGHT, SIDEBAR_WIDTH, group_letters, terrain_type_map
    )

    pygame.display.flip()

def handle_events(config, dt):
    """Handles events (quitting, key presses including Alt+F4, zoom, and continuous camera panning)."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  # Immediately exit on QUIT event.
        elif event.type == pygame.KEYDOWN:
            # Check for Alt+F4 combination.
            if event.key == pygame.K_F4 and (pygame.key.get_mods() & pygame.KMOD_ALT):
                pygame.quit()
                sys.exit()  # Immediately exit on Alt+F4.
            # Handle one-time key presses (non-arrow keys):
            if event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                config['food_respawn_interval'] = min(config['food_respawn_interval'] + 1000, 10000)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                config['food_respawn_interval'] = max(config['food_respawn_interval'] - 1000, 1000)
            elif event.key in (pygame.K_GREATER, pygame.K_PERIOD):
                config['aging_interval'] = min(config['aging_interval'] + 1000, 10000)
            elif event.key in (pygame.K_LESS, pygame.K_COMMA):
                config['aging_interval'] = max(config['aging_interval'] - 1000, 10000)
            elif event.key == pygame.K_1:
                config['simulation_speed'] = min(config['simulation_speed'] + 0.01, 1)
            elif event.key == pygame.K_2:
                config['simulation_speed'] = max(config['simulation_speed'] - 0.01, 0.01)
        elif zoom_manager.handle_zoom(event):
            return False

    # Continuous panning: use key.get_pressed() with delta time.
    keys = pygame.key.get_pressed()
    pan_speed_screen = 200  # Pan speed in screen pixels per second.
    if position_manager is not None:
        pan_movement = pan_speed_screen * dt / zoom_manager.get_scale()  # Convert to world units.
        if keys[pygame.K_LEFT]:
            position_manager.base_x += pan_movement  # Move camera left.
        if keys[pygame.K_RIGHT]:
            position_manager.base_x -= pan_movement  # Move camera right.
        if keys[pygame.K_UP]:
            position_manager.base_y += pan_movement  # Move camera up.
        if keys[pygame.K_DOWN]:
            position_manager.base_y -= pan_movement  # Move camera down.
    
    return False

def close():
    """Closes the pygame screen."""
    pygame.quit()

if __name__ == '__main__':
    import time
    import random

    width = 50
    height = 35
    _terrain, _terrain_color_map, _terrain_type_map = t.generate_heightmap(width, height)
    num_resources = 25

    # Dummy Agents.
    class Agent:
        def __init__(self, x, y, energy=50, group=None):
            self.x = x
            self.y = y
            self.energy = energy
            self.group = group
            self.color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            self.age = 0

        def get_position(self):
            return self.x, self.y

        def calculate_max_energy(self):
            return 100 - self.age

        def is_alive(self):
            return self.energy > 0

    agents = [
        Agent(5, 5, group=0),
        Agent(10, 10, group=1),
        Agent(15, 15, group=0),
    ]

    running = True
    config = {
        'simulation_speed': 0.1,
        'food_respawn_interval': 3000,
        'aging_interval': 5000
    }

    num_groups = 2
    group_letters = [chr(i) for i in range(ord('A'), ord('A') + num_groups)]
    resource_map, resource_locations = r.distribute_resources(_terrain, _terrain_type_map, num_resources)
    terrain_sprites = terrain_renderer.create_terrain_sprites(
        terrain_renderer.TILE_WIDTH, terrain_renderer.TILE_HEIGHT
    )

    clock = pygame.time.Clock()

    while running:
        dt = clock.tick(60) / 1000.0
        # Process events; if a quit event is detected, the program will exit immediately.
        handle_events(config, dt)
        constrained_heights = main.calculate_constrained_heights(_terrain, terrain_renderer.TILE_HEIGHT) #This is what is needed
        update_display(_terrain, _terrain_type_map, resource_map, agents, config, group_letters, terrain_sprites, constrained_heights)
    close()