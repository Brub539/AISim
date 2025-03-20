# vis_components/zoom.py
import pygame

class ZoomManager:
    def __init__(self, initial_scale=2.0, zoom_speed=0.1, min_scale=0.5, max_scale=3.0):
        self.scale = initial_scale
        self.zoom_speed = zoom_speed
        self.min_scale = min_scale
        self.max_scale = max_scale

    def handle_zoom(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Zoom in
                self.scale += self.zoom_speed
            elif event.y < 0:  # Zoom out
                self.scale -= self.zoom_speed
            
            # Constrain the zoom scale within specified limits
            self.scale = max(self.min_scale, min(self.scale, self.max_scale))
            return True  # Signal that zoom changed
        return False  # Signal that zoom didn't change

    def get_scale(self):
        return self.scale