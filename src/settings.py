"""
This file contains the settings for the Neurotrace game.
It includes the game title, window dimensions, and other configurations.
"""

# Game Window Settings
GAME_TITLE = "Neurotrace"
WINDOW_WIDTH = 128
WINDOW_HEIGHT = 128
CURSOR = True
# Frame Rate
FPS = 60

# Camera Settings
CAMERA_DEADZONE = 16  # Reduced deadzone for more responsive camera
CAMERA_SMOOTHING = 0.2  # Increased smoothing for less jitter

# Player Physics Settings
PLAYER_SPEED = 1
PLAYER_JUMP_SPEED = -3
GRAVITY = 0.2
ANIMATION_SPEED = 8  # Frames per animation cycle