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
        "portal": (488, 96, 16, 16),  # Portal at (488, 96) with size 16x16
    },
    1: {
        "playerInitPos": (0, 112),  # Relative Position 
        "mapUV": (0, 256),
        "mapWH": (128*6, 128),
        "mapFloor": [
            (0, 112, 128*6, 16),  # Main floor: (x, y, width, height) / Relative Position
            # (200, 296, 75, 16),   # Platform 1
            # (400, 240, 75, 16),   # Platform 2
        ],
        "enemies": [
            (4, 100, 112),  # type 0 at (100, 352)
            (5, 300, 112),  # type 1 at (300, 352)
            (4, 450, 112),  # type 1 at (450, 352)
            (4, 450, 112),  # type 1 at (450, 352)
            (4, 450, 112),  # type 1 at (450, 352)
        ],
        "mapWall": [
            (0, 256, 8, 128),            # Left wall
            (128*6-8, 256, 16, 128),     # Right wall
        ],
        "portal": (128*6-40, 112-16, 16, 16),  # Portal at (728, 96) with size 16x16
    },
    2: {
        "playerInitPos": (0, 112),  # Relative Position 
        "mapUV": (0, 384),
        "mapWH": (128*8, 128),
        "mapFloor": [
            (0, 112, 128*8, 16),  # Main floor: (x, y, width, height) / Relative Position
            (200, 80, 75, 16),    # Platform 1
            (400, 60, 75, 16),    # Platform 2
            (600, 80, 75, 16),    # Platform 3
        ],
        "enemies": [
            (4, 150, 112),  # type 0 at (150, 112)
            (4, 350, 112),  # type 1 at (350, 112)
            (4, 550, 112),  # type 1 at (550, 112)
            (4, 750, 112),  # type 1 at (750, 112)
            (4, 200, 80),   # type 0 on platform 1
            (4, 600, 80),   # type 1 on platform 3
            (5, 600, 80),   # type 1 on platform 3
            (2, 1000, 80),   # type 2 on platform 3
        ],
        "mapWall": [
            (0, 384, 8, 128),            # Left wall
            (128*8-8, 384, 16, 128),     # Right wall
        ],
        "portal": (128*8-40, 112-16, 16, 16),  # Portal at (984, 96) with size 16x16
    },
    3: {
        "playerInitPos": (0, 112),
        "mapUV": (0, 512),
        "mapWH": (128*10, 128),
        "mapFloor": [
            (0, 112, 128*10, 16),  # Main floor
            (250, 80, 75, 16),    # Platform 1
            # (500, 60, 75, 16),    # Platform 2
            # (750, 80, 75, 16),    # Platform 3
            # (950, 40, 75, 16),    # Platform 4 (higher)
        ],
        "enemies": [
            (4, 200, 112),   # type 0 on main floor
            (5, 400, 112),   # type 1 on main floor
            (4, 600, 112),   # type 0 on main floor
            (5, 800, 112),   # type 1 on main floor
            (2, 1000, 112),  # type 2 on main floor
            (4, 250, 80),    # type 0 on platform 1
            (5, 500, 60),    # type 1 on platform 2
            (4, 750, 80),    # type 0 on platform 3
            (2, 950, 40),    # type 2 on platform 4
        ],
        "mapWall": [
            (0, 512, 8, 128),                # Left wall
            (128*10-8, 512, 16, 128),        # Right wall
        ],
        "portal": (128*10-40, 112-16, 16, 16),  # Portal at (1240, 96)
    },
    4: {
        "playerInitPos": (0, 112),
        "mapUV": (0, 640),
        "mapWH": (128*6, 128),
        "mapFloor": [
            (0, 112, 128*6, 16),  # Main floor
        ],
        "enemies": [
            (8, 600, 112),  # Boss enemy with sniper weapon at center-ish
        ],
        "mapWall": [
            (0, 640, 8, 128),                # Left wall
            (128*6-8, 640, 16, 128),         # Right wall
        ],
        # "portal": (128*6-40, 112-16, 16, 16),  # Portal at (728, 96)
    },
}