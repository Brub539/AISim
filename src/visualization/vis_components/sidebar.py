import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np #Import Numpy, required for visualization
from src.environment.terrain import get_terrain_type, TERRAIN_SAND, TERRAIN_GRASS, TERRAIN_STONE, TERRAIN_SNOW, TERRAIN_WATER

from .scrollbar import Scrollbar, SCROLLBAR_WIDTH # All the variables for now are here

SIDEBAR_COLOR = (50, 50, 50)  # Dark gray
TEXT_COLOR = (255, 255, 255)  # White

# --- Scrollbar (Created ONCE) ---
_scrollbar = None #Global variable, the scrollbar does not reset.

def calculate_isometric_z(x, y):
    """Calculates a Z-position for isometric representation (placeholder)."""
    z = x * 0.5 + y * 0.5
    return z

def create_max_energy_graph(agent):
    """Creates a Pygame surface with a Matplotlib graph of max energy over age."""
    # Only plot up to current age
    ages = np.arange(0, agent.age + 1)
    max_energies = []
    original_age = agent.age

    # Calculate energy values up to current age only
    for age in ages:
        agent.age = age
        max_energy = agent.calculate_max_energy()
        max_energies.append(max_energy)

    agent.age = original_age

    # Create the plot
    fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
    ax.plot(ages, max_energies)
    ax.set_xlabel("Age", fontsize=6)
    ax.set_ylabel("Max Energy", fontsize=6)
    ax.set_title("Max Energy Over Age", fontsize=6)

    # Dynamic axes scaling
    max_y = max(max_energies) if max_energies else 100
    ax.set_ylim(0, max_y * 1.1)
    ax.set_xlim(0, max(agent.age * 1.2, 1))  # Scale x-axis with some padding

    fig.tight_layout()

    # Draw the figure on a canvas
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    s = canvas.tostring_argb()
    size = canvas.get_width_height()

    graph_surface = pygame.image.fromstring(s, size, "RGBA")

    # Delete plot from memory
    plt.close(fig)

    return graph_surface

def draw_agent_info(screen, agent, x, y, agent_index, font, group_letters, config, terrain_type_map):
    """Draws individual agent information."""
    text_color = TEXT_COLOR
    group_letter = group_letters[agent.group]
    agent_name = f"Agent {group_letter}{agent_index + 1}"  # Use group-specific index
    energy_text = f"Energy: {int(agent.energy)} / {int(agent.max_energy)}"  # Shows the Max Energy
    isometric_z = calculate_isometric_z(agent.x, agent.y)  # Calculate the position.
    height_text = f"Height: {int(isometric_z)}"
    age_text = f"Age: {agent.age:.2f}" #Show the age.

    # Check if agent died
    if not agent.is_alive():
        if agent.death_time is not None and agent.birth_time is not None:
            death_time = (agent.death_time - agent.birth_time) / 1000  # Death Time, minus time that born.
            death_text = f"Died at: {death_time:.2f}"
            death_pos_text = f"Death Pos: ({agent.death_x:.2f}, {agent.death_y:.2f})"
        else:
            death_text = "Dead (Time unknown)"
            death_pos_text = ""
        alive_text = "Dead"
    else:
        death_text = ""
        death_pos_text = ""
        alive_text = "Alive"

    # Calculate time since last ate
    if hasattr(agent, 'last_ate'):
        last_ate_time = pygame.time.get_ticks() - agent.last_ate  # Time.
        agent.total_las_ate = f"Last Ate: {int(last_ate_time / 1000)}s ago"  # In seconds.
        last_ate_text = agent.total_las_ate
    else:
        last_ate_text = "Never Ate"

    # Calculate current speed with terrain multiplier
    base_speed = 4.0 * config['simulation_speed']  # Updated to match movement.py base speed
    terrain_multiplier = getattr(agent, 'terrain_speed_multiplier', 1.0)
    current_speed = base_speed * terrain_multiplier
    
    # Get current terrain type and name
    current_terrain = get_terrain_type(terrain_type_map, round(agent.x), round(agent.y))
    terrain_name = {
        TERRAIN_SAND: "Sand",
        TERRAIN_GRASS: "Grass",
        TERRAIN_STONE: "Stone",
        TERRAIN_SNOW: "Snow",
        TERRAIN_WATER: "Water"
    }.get(current_terrain, "Unknown")
    
    speed_text = f"Speed: {current_speed:.2f} tiles/s (x{terrain_multiplier:.1f}) - {terrain_name}"

    # Render the text
    name_surface = font.render(agent_name, True, text_color)
    energy_surface = font.render(energy_text, True, text_color)
    speed_surface = font.render(speed_text, True, text_color)
    last_ate_surface = font.render(last_ate_text, True, text_color)
    height_surface = font.render(height_text, True, text_color)
    age_surface = font.render(age_text, True, text_color)
    alive_surface = font.render(alive_text, True, text_color)

    # Blit the text onto the screen
    screen.blit(name_surface, (x, y))
    screen.blit(energy_surface, (x, y + 25))
    screen.blit(speed_surface, (x, y + 50))
    screen.blit(last_ate_surface, (x, y + 75))
    screen.blit(height_surface, (x, y + 100))
    screen.blit(age_surface, (x, y + 125))
    screen.blit(alive_surface, (x, y + 150))

    # Display death text if applicable
    if death_text:
        death_surface = font.render(death_text, True, text_color)
        death_pos_surface = font.render(death_pos_text, True, text_color)
        screen.blit(death_surface, (x, y + 175))
        if death_pos_text:
            screen.blit(death_pos_surface, (x, y + 200))

def draw_sidebar(screen, agents, font, config, game_width, screen_height, sidebar_width, group_letters, terrain_type_map):
    """Draws the sidebar with agent and simulation information."""

    # --- Scrollbar (Created ONCE) ---
    global _scrollbar # Now a global variable, does not reset.

    # Create a surface to hold all sidebar content
    total_height = calculate_total_height(agents, group_letters)
    sidebar_surface = pygame.Surface((sidebar_width, total_height))
    sidebar_surface.fill(SIDEBAR_COLOR)
    y_offset = 20

    # Display simulation info first
    speed_text = f"Sim Speed: {config['simulation_speed']:.2f}"
    speed_surface = font.render(speed_text, True, TEXT_COLOR)
    sidebar_surface.blit(speed_surface, (10, y_offset))
    y_offset += 30

    respawn_text = f"Food Respawn: {config['food_respawn_interval'] / 1000:.2f}s (+/- keys)"
    respawn_surface = font.render(respawn_text, True, TEXT_COLOR)
    sidebar_surface.blit(respawn_surface, (10, y_offset))
    y_offset += 30

    aging_text = f"Aging Interval: {config['aging_interval'] / 1000:.2f}s (</> keys)"
    aging_surface = font.render(aging_text, True, TEXT_COLOR)
    sidebar_surface.blit(respawn_surface, (10, y_offset))
    y_offset += 50

    # Group agents
    grouped_agents = {}
    for agent in agents:
        if agent.group not in grouped_agents:
            grouped_agents[agent.group] = []
        grouped_agents[agent.group].append(agent)

    # Display each group and its agents
    group_indices = {}  # Dictionary to track indices within each group
    for group_id, agent_list in grouped_agents.items():
        group_color = agent_list[0].color
        group_name = f"Group {group_letters[group_id]} (RGB{group_color})"
        group_surface = font.render(group_name, True, group_color)
        sidebar_surface.blit(group_surface, (10, y_offset + 35))
        y_offset += 60
        group_indices[group_id] = 0

        for agent in agent_list: #Change to start by id from the group id.
            section_height = 450  # Increased height for better visibility
            pygame.draw.rect(sidebar_surface, (45, 45, 45), (5, y_offset, sidebar_width - 10, section_height))

            draw_agent_info(sidebar_surface, agent, 10, y_offset + 10, group_indices[group_id], font, group_letters, config, terrain_type_map)
            group_indices[group_id] += 1

            # Create/update and draw energy graph
            if not hasattr(agent, "energy_graph") or agent.age != agent.last_graph_update:
                agent.energy_graph = create_max_energy_graph(agent)
                agent.last_graph_update = agent.age

            # Position graph below agent info with more padding
            graph_y = y_offset + 150  # Adjusted padding before graph
            sidebar_surface.blit(agent.energy_graph, (10, graph_y))

            y_offset += section_height + 10  # Added padding between sections

    #Handle scroll and others
    global SCROLLBAR_WIDTH  # Adjust as needed
    scrollbar_x = game_width + sidebar_width - SCROLLBAR_WIDTH - 2
    sidebar_x = game_width # X position of sidebar
    sidebar_y = 0 # Y position of sidebar

    # --- Create Scrollbar only if it doesn't exist ---
    if _scrollbar is None:
        _scrollbar = Scrollbar(x=scrollbar_x, y=2, width= SCROLLBAR_WIDTH, height= screen_height)
    _scrollbar.set_viewport_size(calculate_total_height(agents, group_letters), screen_height) #Now with the function

    for event in pygame.event.get():
         _scrollbar.handle_event(event, total_height, screen_height, sidebar_x, sidebar_width, sidebar_y) #Scroll

    # Calculate thumb position
    thumb_y, thumb_height, is_over_scrollbar = _scrollbar.update(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0],total_height,screen_height, sidebar_x, sidebar_width)

    _scrollbar.draw(screen, screen_height, is_over_scrollbar, pygame.mouse.get_pressed()[0])

    # Blit the scrolled portion of the sidebar surface onto the screen
    sidebar_rect = pygame.Rect(game_width, 0, sidebar_width - SCROLLBAR_WIDTH - 4, screen_height)
    screen.blit(sidebar_surface, sidebar_rect, (0, -_scrollbar.get_scroll(), sidebar_width - SCROLLBAR_WIDTH - 4, screen_height))

def calculate_total_height(agents, group_letters):
    """Calculate the total height needed for the sidebar content."""
    height = 100  # Initial height for simulation info

    # Group agents
    grouped_agents = {}
    for agent in agents:
        if agent.group not in grouped_agents:
            grouped_agents[agent.group] = []
        grouped_agents[agent.group].append(agent)

    # Calculate height for each group
    for group_id, agent_list in grouped_agents.items():
        height += 60  # Group header
        height += len(agent_list) * (460)  # Agent sections with padding

    return height