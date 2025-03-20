# src/visualization/vis_components/agent_renderer.py
import pygame

AGENT_COLOR = (255, 0, 0)  # Red
DEAD_AGENT_COLOR = (128, 128, 128)  # Gray color for dead agents

def grid_to_iso(grid_x, grid_y, height, tile_width, tile_height):
    """Converts grid coordinates to isometric screen coordinates."""
    screen_x = (grid_x - grid_y) * tile_width / 2
    screen_y = (grid_x + grid_y) * tile_height / 2 - height
    return screen_x, screen_y

def draw_agents(screen, agents, terrain, position_manager, terrain_sprites, scale=1.0): # Added scale
    """Draws the agents on the screen in isometric projection."""
    font = pygame.font.Font(None, int(20*scale))  # Create a font for agent labels, scale size
    cell_size = position_manager.get_terrain_cell_size()
    tile_width = cell_size * 2 * scale #Scale size to position
    tile_height = cell_size * scale #Scale size to position
    agent_size = position_manager.get_agent_size() * scale #Scale size

    group_indices = {}  # Dictionary to track indices within each group

    for agent in agents:
        x, y = agent.get_position()
        height_value = terrain[int(y), int(x)] * 20 * scale  # Scale height and agent

        screen_x, screen_y = grid_to_iso(x, y, height_value, tile_width, tile_height) #Now scales to position
        screen_x, screen_y = position_manager.get_render_position(screen_x, screen_y)

        # Draw a rectangle for the agent
        agent_x = screen_x + tile_width / 2 - 5*scale #Scale size
        agent_y = screen_y + tile_height / 2 - 10*scale #Scale size

        # Use gray color for dead agents and draw them horizontally
        agent_display_color = DEAD_AGENT_COLOR if not agent.is_alive() else agent.color
        if agent.is_alive():
            pygame.draw.rect(screen, agent_display_color, (int(agent_x), int(agent_y), int(10*scale), int(20*scale))) #Scale size
        else:
            # Draw dead agents horizontally (swapped width and height)
            pygame.draw.rect(screen, agent_display_color, (int(agent_x), int(agent_y + 5*scale), int(20*scale), int(10*scale))) #Scale size

        # Create and render agent label (group letter + number)
        group_letter = chr(ord('A') + agent.group)  # Convert group number to letter (0->A, 1->B, etc)

        # Get the index for this agent within its group
        if agent.group not in group_indices:
            group_indices[agent.group] = 1  # Start index at 1 for each group
        else:
            group_indices[agent.group] += 1
        group_index = group_indices[agent.group] #Set the index

        label_text = f"{group_letter}{group_index}"  # Create label text (e.g., "A1", "A2", "B1")
        label_surface = font.render(label_text, True, (255, 255, 255))  # White text

        # Position label above agent
        label_x = int(agent_x) - label_surface.get_width() // 2 + 5*scale  # Center label horizontally and scale.
        label_y = int(agent_y) - 20*scale  # Position above agent and scale.

        # Draw label with black outline for better visibility
        outline_positions = [(x,y) for x in [-1,1] for y in [-1,1]]
        for dx, dy in outline_positions:
            screen.blit(font.render(label_text, True, (0, 0, 0)), (int(label_x + dx*scale), int(label_y + dy*scale))) #Scale
        screen.blit(label_surface, (label_x, label_y))