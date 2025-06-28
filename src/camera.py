import src.settings

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.deadzone = src.settings.CAMERA_DEADZONE
        self.smoothing = src.settings.CAMERA_SMOOTHING
        self.screen_width = src.settings.WINDOW_WIDTH
        self.screen_height = src.settings.WINDOW_HEIGHT
        
    def update(self, target_x, target_y, map_width=256):
        """Update camera position to follow target with deadzone and smoothing"""
        # Calculate target camera position (center target on screen)
        self.target_x = target_x - self.screen_width // 2
        
        # Apply deadzone - only move camera if target is outside deadzone
        current_center = self.x + self.screen_width // 2
        distance_from_center = abs(target_x - current_center)
        
        if distance_from_center > self.deadzone:
            # Smoothly move camera towards target
            self.x += (self.target_x - self.x) * self.smoothing
        else:
            # If within deadzone, snap to target for stability
            self.x = self.target_x
        
        # Clamp camera to map boundaries
        self.x = max(0, min(self.x, map_width - self.screen_width))
        
        # For now, keep Y at 0 (no vertical camera movement)
        self.y = 0
        
    def get_offset(self):
        """Get the camera offset for drawing, as integers to avoid jitter"""
        return int(self.x), int(self.y) 