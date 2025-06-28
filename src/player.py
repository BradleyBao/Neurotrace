import pyxel, src.structure, src.settings
import math

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
        # Dash system
        self.is_dashing = False
        self.dash_distance = 32  # pixels
        self.dash_speed = 6
        self.dash_cooldown = 0
        self.dash_cooldown_max = 20  # frames
        self.dash_remaining = 0
        # Weapon system
        self.weapon_offset = 5  # 1/3 of 16px
        # 8 directions: [L, R, R45U, L45U, L45D, R45D, D, U]
        self.weapon_sprites = [
            (0, 128),   # Left
            (8, 128),   # Right
            (0, 136),   # Right 45 Up
            (8, 136),   # Left 45 Up
            (16, 128),  # Left 45 Down
            (24, 128),  # Right 45 Down
            (16, 136),  # Down
            (24, 136),  # Up
        ]
        self.weapon_fire_sprites = [
            (32, 128),  # Left
            (40, 128),  # Right
            (32, 136),  # Right 45 Up
            (40, 136),  # Left 45 Up
            (48, 128),  # Left 45 Down
            (56, 128),  # Right 45 Down
            (48, 136),  # Down
            (56, 136),  # Up
        ]
        self.weapon_w = 8
        self.weapon_h = 8
        # Firing logic
        self.is_firing = False
        self.fire_timer = 0
        self.fire_duration = 6  # frames (about 100ms at 60fps)
        self.fire_direction_idx = 1
        self.fire_angle = 0
        self.fire_line = None  # (x0, y0, x1, y1)
        # Load animation frames
        self.loadAnimation()

    def loadAnimation(self):
        self.walk_left = [(48, 0), (64, 0)]
        self.walk_right = [(80, 0), (96, 0)]
        self.stand_frame_left = self.playerLeft
        self.stand_frame_right = self.playerRight

    def moveLeft(self):
        if not self.is_dashing:
            self.x -= self.speed
        self.is_moving = True

    def moveRight(self):
        if not self.is_dashing:
            self.x += self.speed
        self.is_moving = True

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_speed
            self.is_jumping = True

    def dash(self):
        if not self.is_dashing and self.dash_cooldown == 0:
            self.is_dashing = True
            self.dash_remaining = self.dash_distance
            self.dash_cooldown = self.dash_cooldown_max

    def fire(self):
        if not self.is_firing:
            self.is_firing = True
            self.fire_timer = self.fire_duration
            self.fire_direction_idx = self.get_weapon_direction_index()
            # Store the angle for the shot
            player_cx = self.x + 8
            player_cy = self.y + 8
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            self.fire_angle = math.atan2(my - player_cy, mx - player_cx)
            # Calculate the line end (blocked by floor)
            self.fire_line = self.calculate_fire_line(self.fire_angle)

    def update(self, level=0):
        # Mouse-based facing
        player_cx = self.x + 8
        player_cy = self.y + 8
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        dx = mouse_x - player_cx
        # Facing is right if mouse is to the right, else left
        self.facing_direction = 1 if dx >= 0 else -1
        # Dash logic
        if self.is_dashing:
            dash_step = min(self.dash_speed, self.dash_remaining)
            self.x += dash_step * self.facing_direction
            self.dash_remaining -= dash_step
            if self.dash_remaining <= 0:
                self.is_dashing = False
        elif self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        # Firing logic
        if self.is_firing:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.is_firing = False
                self.fire_line = None
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

    def calculate_fire_line(self, angle):
        # Start at gun muzzle
        player_cx = self.x + 8
        player_cy = self.y + 8
        muzzle_x = int(player_cx + math.cos(angle) * 8)
        muzzle_y = int(player_cy + math.sin(angle) * 8)
        # Step along the line until hit floor or screen edge
        max_length = 128  # screen size
        step = 2
        for l in range(0, max_length, step):
            tx = int(muzzle_x + math.cos(angle) * l)
            ty = int(muzzle_y + math.sin(angle) * l)
            # Check screen bounds
            if tx < 0 or tx >= 128 or ty < 0 or ty >= 128:
                return (muzzle_x, muzzle_y, tx, ty)
            # Check collision with floors
            for floor in self.structure[self.level]["mapFloor"]:
                fx, fy, fw, fh = floor
                if fx <= tx < fx+fw and fy <= ty < fy+fh:
                    return (muzzle_x, muzzle_y, tx, ty)
        # No collision, go to max
        tx = int(muzzle_x + math.cos(angle) * max_length)
        ty = int(muzzle_y + math.sin(angle) * max_length)
        return (muzzle_x, muzzle_y, tx, ty)

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
        self.is_dashing = False
        self.dash_cooldown = 0
        self.dash_remaining = 0

    def get_weapon_direction_index(self):
        # 8 directions: [L, R, R45U, L45U, L45D, R45D, D, U]
        player_cx = self.x + 8
        player_cy = self.y + 8
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        angle = math.degrees(math.atan2(my - player_cy, mx - player_cx))
        # Map angle to -180 to 180
        # Map to 8 directions
        # Sectors: (centered on L, R, R45U, L45U, L45D, R45D, D, U)
        # L: 157.5 to -157.5
        # L45U: 112.5 to 157.5
        # U: 67.5 to 112.5
        # R45U: 22.5 to 67.5
        # R: -22.5 to 22.5
        # R45D: -67.5 to -22.5
        # D: -112.5 to -67.5
        # L45D: -157.5 to -112.5
        if angle > 157.5 or angle <= -157.5:
            return 0  # Left
        elif -22.5 < angle <= 22.5:
            return 1  # Right
        elif 22.5 < angle <= 67.5:
            return 5  # Right 45 Up
        elif 67.5 < angle <= 112.5:
            return 6  # Up
        elif 112.5 < angle <= 157.5:
            return 4  # Left 45 Up
        elif -67.5 < angle <= -22.5:
            return 2  # Right 45 Down
        elif -112.5 < angle <= -67.5:
            return 7  # Down
        elif -157.5 < angle <= -112.5:
            return 3  # Left 45 Down
        else:
            return 1  # Default to Right

    def draw_weapon(self):
        if self.is_firing:
            idx = self.fire_direction_idx
            sx, sy = self.weapon_fire_sprites[idx]
        else:
            idx = self.get_weapon_direction_index()
            sx, sy = self.weapon_sprites[idx]
        # Weapon position: offset from player center, in direction of mouse
        player_cx = self.x + 8
        player_cy = self.y + 8
        if self.is_firing:
            angle = self.fire_angle
        else:
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            angle = math.atan2(my - player_cy, mx - player_cx)
        wx = int(player_cx + math.cos(angle) * 8 - self.weapon_w // 2)
        wy = int(player_cy + math.sin(angle) * 8 - self.weapon_h // 2)
        pyxel.blt(wx, wy, 0, sx, sy, self.weapon_w, self.weapon_h, 14)
        # Draw shooting line if firing
        if self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            pyxel.line(x0, y0, x1, y1, 7)  # color 7 (white)

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
        # Draw weapon after player
        self.draw_weapon()