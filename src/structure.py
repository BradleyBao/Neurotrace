STRUCTURE = {
    0: {
        "playerInitPos": (0, 95),
        "mapUV": (0, 128),
        "mapWH": (128*4, 128),
        "mapFloor": [
            (0, 112, 128*4, 16),  # Main floor: (x, y, width, height)
            (150, 40, 75, 16),    # Platform 1
            # (80, 80, 48, 16),   # Platform 2
        ],
        "enemies": [
            (4, 5*8, 95),  # type 0 at (40, 95)
            (4, 320, 95),  # type 1 at (80, 95)
            (4, 320, 95),  # type 1 at (80, 95)
            (4, 320, 95),  # type 1 at (80, 95)
            # Add more as needed
        ],
        "mapWall": [
            (0, 0, 8, 128),            # Left wall
            (128*4-8, 0, 16, 128),     # Right wall
        ],
        "portal": (488, 96, 16, 16),  # Portal at (488, 224) with size 16x16
    },
    1: {
        "playerInitPos": (0, 112),  # Relative Position 
        "mapUV": (0, 256),
        "mapWH": (128*4, 128),
        "mapFloor": [
            (0, 112, 128*4, 16),  # Main floor: (x, y, width, height) / Relative Position
            (200, 296, 75, 16),   # Platform 1
            (400, 240, 75, 16),   # Platform 2
        ],
        "enemies": [
            (4, 100, 352),  # type 0 at (100, 352)
            (4, 300, 352),  # type 1 at (300, 352)
            (4, 450, 352),  # type 1 at (450, 352)
        ],
        "mapWall": [
            (0, 256, 8, 128),            # Left wall
            (128*4-8, 256, 16, 128),     # Right wall
        ],
    },
}