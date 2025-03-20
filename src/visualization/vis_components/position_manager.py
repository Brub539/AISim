# src/visualization/position_manager.py

class PositionManager:
    def __init__(self, game_width, screen_height, map_width, map_height, vertical_offset=300):
        """Initialize the position manager with screen dimensions and map dimensions."""
        self.game_width = game_width
        self.screen_height = screen_height
        # Set the base offset so that the center of the map (map_width/2, map_height/2)
        # maps to (0,0) in world coordinates.
        self.base_x = -map_width / 2
        self.base_y = -map_height / 2
        self.zoom = 1.0  # Zoom level for the entire simulation
        self.vertical_offset = vertical_offset

    def set_base_position(self, x, y):
        """Set the base position for the entire simulation view."""
        self.base_x = x
        self.base_y = y

    def set_zoom(self, zoom):
        """Set the zoom level for the entire simulation."""
        self.zoom = max(0.1, min(zoom, 5.0))  # Limit zoom between 0.1x and 5x

    def get_render_position(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates,
        ensuring the map center is at the center of the game area.
        """
        # Apply base offset and zoom
        screen_x = (world_x + self.base_x) * self.zoom
        screen_y = (world_y + self.base_y) * self.zoom

        # Shift so that (0,0) is the center of the game area
        screen_x += self.game_width // 2
        screen_y += self.screen_height // 2
        #shift upward by vertical_offset
        screen_y -= self.vertical_offset

        return screen_x, screen_y

    def get_terrain_cell_size(self):
        """Get the size of terrain cells based on zoom level."""
        base_size = 20  # Base cell size in pixels
        return base_size * self.zoom

    def get_resource_size(self):
        """Get the size of resource indicators based on zoom level."""
        base_size = 10  # Base resource size in pixels
        return base_size * self.zoom

    def get_agent_size(self):
        """Get the size of agent indicators based on zoom level."""
        base_size = 15  # Base agent size in pixels
        return base_size * self.zoom
