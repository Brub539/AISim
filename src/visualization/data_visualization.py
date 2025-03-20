# src/visualization/data_visualization.py
import pygame
import matplotlib.pyplot as plt
import numpy as np
from src.agent.agent import Agent  # Example
from src.environment import resource
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Sidebar colors
SIDEBAR_COLOR = (50, 50, 50)  # Dark gray
TEXT_COLOR = (255, 255, 255)  # White

def collect_agent_data(agents):
    """Collects data from the agents."""
    agent_energies = [agent.energy for agent in agents]
    return agent_energies

def create_energy_histogram(agent_energies):
    """Creates a histogram of agent energy levels."""
    plt.hist(agent_energies, bins=10, color='skyblue', edgecolor='black')
    plt.xlabel("Energy Level")
    plt.ylabel("Number of Agents")
    plt.title("Agent Energy Distribution")
    plt.show()  # Show plot.

def display_data(screen, font, agents, x, y):
    agent_energies = collect_agent_data(agents)
    average_energy = np.mean(agent_energies)

    average_energy_text = f"Average Energy: {average_energy:.2f}"
    average_energy_surface = font.render(average_energy_text, True, (255, 255, 255))
    screen.blit(average_energy_surface, (x, y))

def draw_agent_info(screen, agent, x, y, agent_index, font):
    """Draws individual agent information."""
    text_color = TEXT_COLOR
    agent_name = f"Agent {agent_index + 1}"  # Agent number
    energy_text = f"Energy: {int(agent.energy)} / {int(agent.max_energy)}"  # Shows the Max Energy
    isometric_z = calculate_isometric_z(agent.x, agent.y)  # Calculate the position.
    height_text = f"Height: {isometric_z:.2f}"

    # Check if agent died
    if hasattr(agent, 'death_time') and agent.death_time is not None:
        death_time = (agent.death_time - agent.birth_time) / 1000  # Death Time, minus time that born.
        death_text = f"Died at: {death_time:.2f}"
        death_pos_text = f"Death Pos: ({agent.death_x:.2f}, {agent.death_y:.2f})"
    else:
        death_text = "Alive"
        death_pos_text = ""

    # Calculate time since last ate (you need to implement this in the Agent class)
    if hasattr(agent, 'last_ate'):
        last_ate_time = pygame.time.get_ticks() - agent.last_ate  # Time.
        last_ate_text = f"Last Ate: {last_ate_time / 1000:.2f}s ago"  # In seconds.
    else:
        last_ate_text = "Never Ate"

    # Render the text
    name_surface = font.render(agent_name, True, text_color)
    energy_surface = font.render(energy_text, True, text_color)
    last_ate_surface = font.render(last_ate_text, True, text_color)
    death_surface = font.render(death_text, True, text_color)
    death_pos_surface = font.render(death_pos_text, True, text_color)
    height_surface = font.render(height_text, True, text_color)

    # Blit the text onto the screen
    screen.blit(name_surface, (x, y))
    screen.blit(energy_surface, (x, y + 25))
    screen.blit(last_ate_surface, (x, y + 50))
    screen.blit(death_surface, (x, y + 75))
    screen.blit(height_surface, (x, y + 100)) #Height is closer now

def calculate_isometric_z(x, y):
    """Calculates a Z-position for isometric representation (placeholder)."""
    # This is a placeholder - replace with actual isometric calculation.
    # You'll need to adjust this based on your terrain/isometric projection.

    # Example: (the higher the x and y position are, the higher the isometric calculation will be.)
    z = x * 0.5 + y * 0.5
    return z

def create_max_energy_graph(agent):
    """Creates a Pygame surface with a Matplotlib graph of max energy over age."""
    # Get the list of ages, then get the max_energy to create a list.
    max_age = 100  # Test value.
    ages = np.arange(0, max_age)
    max_energies = []

    # Set the values, based on ages, with a scale of 1 to max.
    for age in ages:
        agent.age = age  # Change its age.
        max_energy = agent.calculate_max_energy()  # Calculate the new value.
        max_energies.append(max_energy)  # Append it to the array.
        # agent.age = 0 #Reset back.

    # Create the plot.
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)  # set the size.
    ax.plot(ages, max_energies)  # Plot
    ax.set_xlabel("Age", fontsize=8)  # Set labels
    ax.set_ylabel("Max Energy", fontsize=8)  # Set labels.
    ax.set_title("Max Energy Over Age", fontsize=8)  # Set the title.
    fig.tight_layout()  # Adjust layout to prevent labels from overlapping

    # Draw the figure on a canvas
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    s = canvas.tostring_argb()
    size = canvas.get_width_height()

    graph_surface = pygame.image.fromstring(s, size, "RGBA")

    # Delete plot from memory.
    plt.close(fig)

    return graph_surface