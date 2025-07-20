# Neurotrace
**This project is for Fundamental of Information Technology 2 in Keio SFC.**

A 2D platformer game built with Pyxel featuring a smooth camera system that follows the player.

## Features

### Camera System
- **Smooth Following**: The camera smoothly follows the player with configurable smoothing
- **Deadzone**: Camera only moves when the player is outside a configurable deadzone from screen center
- **Bounds Clamping**: Camera is clamped to map boundaries to prevent showing empty space
- **Tile-based Scrolling**: Map scrolling is optimized for tile-based graphics

### Player Controls
- **Movement**: A/D keys for left/right movement
- **Jump**: Spacebar to jump
- **Dash**: Ctrl key for quick dash movement
- **Shoot**: Left mouse button to fire weapon in the direction of the mouse cursor

### Game Features
- **Platformer Physics**: Gravity, jumping, and collision detection
- **Weapon System**: 8-directional weapon aiming with mouse
- **Animation**: Walking and standing animations for the player
- **Level System**: Support for multiple levels with different layouts

## Camera Settings

The camera behavior can be customized in `src/settings.py`:

```python
CAMERA_SMOOTHING = 0.1  # How smoothly the camera follows (0.0 = instant, 1.0 = no movement)
CAMERA_DEADZONE = 32    # Pixels from center before camera starts moving
```

## Running the Game

```bash
python main.py
```

## Controls

- **A/D**: Move left/right
- **Space**: Jump
- **Ctrl**: Dash
- **Left Mouse**: Fire weapon
- **Mouse**: Aim weapon

## Level Structure

Levels are defined in `src/structure.py` with:
- Player starting position
- Map tile data location
- Map dimensions
- Floor/platform collision data

The current level includes:
- A main floor spanning the entire level width
- Three floating platforms for vertical gameplay
- Extended map width (256 pixels) to demonstrate camera scrolling 
