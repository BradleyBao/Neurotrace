import pyxel, src.structure, src.settings

class Player:
    def __init__(self):
        self.structure = src.structure.STRUCTURE
        self.x = 0
        self.y = 0
        self.level = 0
        self.speed = src.settings.PLAYER_SPEED
        self.jump_speed = src.settings.PLAYER_JUMP_SPEED
        self.gravity = src.settings.GRAVITY
        self.velocity_y = 0
        self.is_jumping = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.facing_direction = 1  # 1 for right, -1 for left
        self.is_moving = False

        self.playerLeft = (16, 0)
        self.playerRight = (32, 0)
        
        # Load animation frames
        self.loadAnimation()

    def loadAnimation(self):
        self.walk_left = [(48, 0), (64, 0)]
        self.walk_right = [(80, 0), (96, 0)]
        self.stand_frame_left = self.playerLeft
        self.stand_frame_right = self.playerRight

    def moveLeft(self):
        self.x -= self.speed
        self.facing_direction = -1
        self.is_moving = True

    def moveRight(self):
        self.x += self.speed
        self.facing_direction = 1
        self.is_moving = True

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_speed
            self.is_jumping = True

    def update(self, level=0):
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # Check floor collision
        self.checkFloorCollision(level)
        
        # Update animation - continue animation while moving
        if self.is_moving:
            self.animation_timer += 1
            if self.animation_timer >= src.settings.ANIMATION_SPEED:  # Animation speed
                self.animation_frame = (self.animation_frame + 1) % 2
                self.animation_timer = 0
        else:
            # Reset animation when not moving
            self.animation_frame = 0
            self.animation_timer = 0

    def checkFloorCollision(self, level):
        floors = self.structure[level]["mapFloor"]
        
        # Check if player is on any floor
        on_floor = False
        for i, floor in enumerate(floors):
            floor_x, floor_y, floor_w, floor_h = floor
            
            # Check if player is above the floor and falling
            if (self.x < floor_x + floor_w and 
                self.x + 16 > floor_x and 
                self.y + 16 >= floor_y and 
                self.y + 16 <= floor_y + floor_h + 5):  # Added tolerance for landing
                
                # Land on floor
                self.y = floor_y - 16
                self.velocity_y = 0
                self.is_jumping = False
                on_floor = True
                break
        
        # If not on any floor, player is jumping
        if not on_floor:
            self.is_jumping = True

    def resetPlayerPos(self, level=0):
        self.x = self.structure[level]["playerInitPos"][0]
        self.y = self.structure[level]["playerInitPos"][1]
        self.velocity_y = 0
        self.is_jumping = False
        self.animation_frame = 0
        self.animation_timer = 0

    def draw(self):
        if self.is_moving:
            # Draw walking animation
            if self.facing_direction == 1:  # Right
                frame = self.walk_right[self.animation_frame]
            else:  # Left
                frame = self.walk_left[self.animation_frame]
            pyxel.blt(self.x, self.y, 0, frame[0], frame[1], 16, 16, 14)
        else:
            # Draw standing frame based on facing direction
            if self.facing_direction == 1:  # Right
                pyxel.blt(self.x, self.y, 0, self.stand_frame_right[0], self.stand_frame_right[1], 16, 16, 14)
            else:  # Left
                pyxel.blt(self.x, self.y, 0, self.stand_frame_left[0], self.stand_frame_left[1], 16, 16, 14)