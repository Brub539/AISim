import numpy as np
from src.environment.terrain import is_walkable, calculate_slope, get_height, TERRAIN_WATER
from src.environment.resource import get_resource_amount, deplete_resource
from src.agent import movement
import pygame
import random
from scipy.special import beta as beta_function  # Import the beta function

class Agent:
    def __init__(self, x, y, energy=100, group=None):
        """Initializes an agent with a starting position and energy."""
        self.x = x
        self.y = y
        self.energy = energy
        self.collected_resources = 0
        self.target_resource = None  # (x, y) of the resource
        self.attempts_to_reach = 0
        self.max_attempts = 50  # Set max attempts to move.
        self.birth_time = pygame.time.get_ticks()  # Set the time that agent was born at.
        self.last_ate = self.birth_time  # Time of last eating = time born.
        self.death_time = None  # Time it died.
        self.death_x = None  # Position that died.
        self.death_y = None  # Position that died.
        self.age = 0  # Age, for beta calculation
        self.group = group  # Group for this agent.
        self.last_age_update = self.birth_time  # Track when to update.
        self.last_graph_update = -1  # Track if the graph was made.
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Set color.
        self.total_las_ate = "Never Ate"
        self.last_eat_update = self.birth_time  # Track when to update last_eat string on sidebar.
        self.last_food = 0

        # Parameters for the beta distribution (adjust as needed)
        self.alpha = 2
        self.beta = 5
        self.max_age = 100  # Max value.

        # Calculate max energy using beta values.
        self.max_energy = self.calculate_max_energy()  # The maximum energy

    def update(self, terrain, terrain_type_map, resource_map, delta, water_flow=None):
        """
        Updates the agent's state (e.g., finds nearest resource and moves towards it).
        If water_flow is provided, and the agent is on a water cell,
        the agent's position is adjusted by the water's flow vector.
        """
        if self.energy <= 0:
            # Set death information
            if self.death_time is None:  # So that we do not update multiple times.
                self.death_time = pygame.time.get_ticks()  # Time
                self.death_x = self.x  # Position.
                self.death_y = self.y  # Position
            return False  # Agent is dead

        # Base metabolism - reduced energy loss for better survival
        current_time = pygame.time.get_ticks()
        time_since_last_update = (current_time - self.last_age_update) / 1000.0  # Convert to seconds
        energy_loss = time_since_last_update * 0  # Reduced to 0.3 energy per second
        self.energy = max(0, self.energy - energy_loss)
        self.last_age_update = current_time

        # Movement logic (delegate to movement.py)
        resource_map = movement.move_towards_resource(self, terrain, terrain_type_map, resource_map, delta)

        # Water effect: if water_flow is provided and the agent is on water, apply drift.
        if water_flow is not None:
            # Convert agent position to integer cell indices.
            ix = int(self.x)
            iy = int(self.y)
            if 0 <= ix < terrain.shape[1] and 0 <= iy < terrain.shape[0]:
                if terrain_type_map[iy, ix] == TERRAIN_WATER:
                    vx, vy = water_flow[iy, ix]
                    # Adjust position by the water's flow vector scaled by delta.
                    self.x += vx * delta
                    self.y += vy * delta

        return resource_map  # Return updated resource map

    def is_alive(self):
        """Returns True if the agent's energy is above zero."""
        return self.energy > 0

    def get_position(self):
        """Returns the agent's current (x, y) coordinates."""
        return self.x, self.y

    def get_energy(self):
        """Returns the agent's current energy level."""
        return self.energy

    def calculate_max_energy(self):
        """Calculates the maximum energy based on a beta distribution and age."""
        x = self.age / self.max_age  # Normalize

        # The PDF
        pdf = (x**(self.alpha - 1) * (1 - x)**(self.beta - 1)) / beta_function(self.alpha, self.beta)
        
        # Ensure the value to be inside our requirements.
        max_energy = (pdf * 90) + 10  # Scale to 90 and shift to start at 10
        
        # Add noise; do not add noise if it's higher or lower than requirements.
        noise = random.uniform(-5, 5)  # Create noise.
        
        # Verify the range of the value.
        if max_energy + noise > 0 and max_energy + noise < 100:
            max_energy += noise

        return max_energy
    
    def adjust_energy_level(self):
        """Adjusts the agent's energy level towards max_energy if current energy exceeds it."""
        if self.energy > self.max_energy:
            self.energy = self.max_energy
