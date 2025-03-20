# src/visualization/vis_components/scrollbar.py
import pygame

SCROLLBAR_WIDTH = 10
SCROLLBAR_COLOR = (80, 80, 80)
SCROLLBAR_HOVER_COLOR = (100, 100, 100)
SCROLLBAR_DRAG_COLOR = (120, 120, 120)

class Scrollbar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._scroll_y = 0.0  # Floating-point scroll position
        self._is_dragging_scrollbar = False
        self.drag_start_y = 0  # Initialize drag_start_y

    def handle_event(self, event, content_height, viewport_height, sidebar_x, sidebar_width, sidebar_y):
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            is_over_sidebar = (
                mouse_pos[0] >= sidebar_x and
                mouse_pos[0] <= sidebar_x + sidebar_width and
                mouse_pos[1] >= sidebar_y and
                mouse_pos[1] <= sidebar_y + viewport_height
            )

            if is_over_sidebar:
                total_scroll = event.y
                if total_scroll != 0:
                    SCROLL_SPEED = 15  # Adjust for desired speed
                    self._scroll_y += total_scroll * SCROLL_SPEED
                    self._scroll_y = max(-(content_height - viewport_height), min(0, self._scroll_y)) #Clamp it.
                    return True
        return False

    def update(self, mouse_pos, mouse_pressed, content_height, viewport_height, sidebar_x, sidebar_width):
        """Updates the scrollbar state based on user interaction."""
        # Calculate scrollbar metrics
        scroll_ratio = viewport_height / content_height
        thumb_height = max(40, viewport_height * scroll_ratio)
        scroll_track_height = viewport_height - 4  # Padding

        # Calculate thumb position
        if content_height > viewport_height:
            scroll_range = content_height - viewport_height
            scroll_percent = -self._scroll_y / scroll_range
            thumb_y = 2 + (scroll_track_height - thumb_height) * scroll_percent
        else:
            thumb_y = 2

        # Check if mouse is over scrollbar
        is_over_scrollbar = (
            mouse_pos[0] >= self.x and
            mouse_pos[0] <= self.x + self.width and
            mouse_pos[1] >= thumb_y and
            mouse_pos[1] <= thumb_y + thumb_height
        )

        # Check if mouse is within the sidebar
        is_over_sidebar = (
            mouse_pos[0] >= sidebar_x and
            mouse_pos[0] <= sidebar_x + sidebar_width
        )

        # Mouse over the scroll bar OR mouse click is within sidebar
        if mouse_pressed and (is_over_scrollbar or is_over_sidebar) and not self._is_dragging_scrollbar:
            self._is_dragging_scrollbar = True
            self.drag_start_y = mouse_pos[1]  # Record initial mouse Y position

        elif not mouse_pressed:
            self._is_dragging_scrollbar = False

        # If is dragging scroll continue.
        if self._is_dragging_scrollbar:
            # Calculate new scroll position based on mouse movement
            delta_y = mouse_pos[1] - self.drag_start_y #How much the mouse is moved.
            self._scroll_y -= delta_y #Set to scroll Y #INVERT
            self._scroll_y = max(-(content_height - viewport_height), min(0, self._scroll_y)) #Clamp it.
            self.drag_start_y = mouse_pos[1]  # Update starting position

        return thumb_y, thumb_height, is_over_scrollbar

    def draw(self, screen, viewport_height, is_over_scrollbar, mouse_pressed):
        """Draws the scrollbar with appropriate styles and handle colors"""

        # Get metrics
        scroll_track_height = viewport_height - 4  # Padding
        scroll_scrollbar_x = self.x
        thumb_y, thumb_height, over_scrollbar = self.update(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0], self.content_height, self.viewport_height, 0, 0) #Fix
        #print(f"thumb_y: {thumb_y}, thumb_height: {thumb_height}")

        # Draw scrollbar track
        pygame.draw.rect(screen, SCROLLBAR_COLOR,
                        (scroll_scrollbar_x, 2, self.width, scroll_track_height))

        # Draw scrollbar thumb with hover effect
        thumb_color = SCROLLBAR_DRAG_COLOR if self._is_dragging_scrollbar else (
            SCROLLBAR_HOVER_COLOR if is_over_scrollbar else SCROLLBAR_COLOR
        )
        pygame.draw.rect(screen, thumb_color,
                        (scroll_scrollbar_x, thumb_y, self.width, thumb_height))

    def set_viewport_size(self, content_height, viewport_height):
        self.content_height = content_height
        self.viewport_height = viewport_height

    def get_scroll(self):
        return self._scroll_y #Return Float!

    def set_scroll(self, scroll_y):
        self._scroll_y = scroll_y