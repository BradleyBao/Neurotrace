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
        self.dash_direction = 1  # 1 for right, -1 for left
        # Weapon system
        self.weapons = [
            {'name': 'Pistol', 'color': 0, 'penetrate': False},
            {'name': 'Rifle', 'color': 12, 'penetrate': True},
            {'name': 'Sniper', 'color': 8, 'penetrate': True},
        ]
        self.current_weapon = 0
        self.bullets = []  # List of bullets: {'x', 'y', 'vx', 'vy', 'color', 'penetrate', 'alive'}
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
        self.fire_angle = 0
        self.fire_line = None  # (x0, y0, x1, y1)
        # Load animation frames
        self.loadAnimation()
        self.health = 400
        self.max_health = 400
        self.alive = True
        self.is_shielding = False
        self.normal_speed = self.speed
        self.shield_speed = 0.2  # Dramatically slower
        self.shield_stamina = 600  # 10 seconds at 60fps
        self.shield_stamina_max = 600
        self.shield_cooldown = 0  # frames
        self.shield_cooldown_max = 600  # 10 seconds

    def loadAnimation(self):
        self.walk_left = [(48, 0), (64, 0)]
        self.walk_right = [(80, 0), (96, 0)]
        self.stand_frame_left = self.playerLeft
        self.stand_frame_right = self.playerRight

    def moveLeft(self):
        if not self.is_dashing:
            if self.is_shielding:
                self.x -= self.shield_speed
            else:
                self.x -= self.speed
        self.is_moving = True
        self.dash_direction = -1

    def moveRight(self):
        if not self.is_dashing:
            if self.is_shielding:
                self.x += self.shield_speed
            else:
                self.x += self.speed
        self.is_moving = True
        self.dash_direction = 1

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_speed
            self.is_jumping = True

    def dash(self):
        if not self.is_dashing and self.dash_cooldown == 0:
            self.is_dashing = True
            self.dash_remaining = self.dash_distance
            self.dash_cooldown = self.dash_cooldown_max

    def fire(self, camera_x=0):
        if not self.is_firing:
            self.is_firing = True
            self.fire_timer = self.fire_duration
            player_screen_x = self.x - camera_x + 8
            player_screen_y = self.y + 8
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            angle = math.atan2(my - player_screen_y, mx - player_screen_x)
            weapon = self.weapons[self.current_weapon]
            # Update weapon sprites for visual model
            if weapon['name'] == 'Pistol':
                self.weapon_sprites = [
                    (0, 128), (8, 128), (0, 136), (8, 136), (16, 128), (24, 128), (16, 136), (24, 136)
                ]
                self.weapon_fire_sprites = [
                    (32, 128), (40, 128), (32, 136), (40, 136), (48, 128), (56, 128), (48, 136), (56, 136)
                ]
            elif weapon['name'] == 'Rifle':
                self.weapon_sprites = [
                    (0, 160), (8, 160), (0, 168), (8, 168), (16, 160), (24, 160), (16, 168), (24, 168)
                ]
                self.weapon_fire_sprites = [
                    (32, 160), (40, 160), (32, 168), (40, 168), (48, 160), (56, 160), (48, 168), (56, 168)
                ]
            elif weapon['name'] == 'Sniper':
                self.weapon_sprites = [
                    (0, 176), (8, 176), (0, 184), (8, 184), (16, 176), (24, 176), (16, 184), (24, 184)
                ]
                self.weapon_fire_sprites = [
                    (32, 176), (40, 176), (32, 184), (40, 184), (48, 176), (56, 176), (48, 184), (56, 184)
                ]
            if weapon['name'] == 'Sniper':
                self.fire_angle = angle
                self.fire_line = self.calculate_fire_line(angle, camera_x)
            else:
                speed = 8 if weapon['name'] == 'Rifle' else 5
                bullet = {'x': self.x + 8 + math.cos(angle) * 2,
                          'y': self.y + 8 + math.sin(angle) * 2,
                          'vx': math.cos(angle) * speed,
                          'vy': math.sin(angle) * speed,
                          'color': weapon['color'],
                          'penetrate': weapon['penetrate'],
                          'alive': True,
                          'damage': 1 if weapon['name']=='Pistol' else 2}
                if weapon['name'] == 'Rifle':
                    bullet['penetrate_count'] = 2
                self.bullets.append(bullet)

    def update(self, level=0, camera_x=0, enemies=None):
        # Mouse-based facing
        player_cx = self.x + 8
        player_cy = self.y + 8
        mouse_x = pyxel.mouse_x + camera_x
        mouse_y = pyxel.mouse_y
        dx = mouse_x - player_cx
        # Facing is right if mouse is to the right, else left
        self.facing_direction = 1 if dx >= 0 else -1
        # Dash logic
        if self.is_dashing:
            dash_step = min(self.dash_speed, self.dash_remaining)
            self.x += dash_step * self.dash_direction
            self.dash_remaining -= dash_step
            if self.dash_remaining <= 0:
                self.is_dashing = False
        elif self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        # Weapon switching
        if pyxel.btnp(pyxel.KEY_Q):
            self.current_weapon = (self.current_weapon - 1) % len(self.weapons)
        if pyxel.btnp(pyxel.KEY_E):
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
        # Firing logic
        if self.is_firing:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.is_firing = False
                self.fire_line = None
        # Update bullets
        for bullet in self.bullets:
            if not bullet['alive']:
                continue
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            # Remove if out of bounds
            if bullet['x'] < 0 or bullet['x'] > 2560 or bullet['y'] < 0 or bullet['y'] > 128:
                bullet['alive'] = False
            # Bullet collision with map floors
            for floor in self.structure[level]['mapFloor']:
                fx, fy, fw, fh = floor
                if fx <= bullet['x'] <= fx+fw and fy <= bullet['y'] <= fy+fh:
                    bullet['alive'] = False
            # Bullet collision with map walls
            for wall in self.structure[level]['mapWall']:
                wx, wy, ww, wh = wall
                if wx <= bullet['x'] <= wx+ww and wy <= bullet['y'] <= wy+wh:
                    bullet['alive'] = False
            # Bullet collision with enemies
            if enemies:
                for enemy in enemies:
                    if not enemy.alive:
                        continue
                    if (enemy.x < bullet['x'] < enemy.x+16 and enemy.y < bullet['y'] < enemy.y+16):
                        enemy.take_damage(bullet.get('damage', 1))
                        if bullet.get('penetrate_count') is not None:
                            bullet['penetrate_count'] -= 1
                            if bullet['penetrate_count'] <= 0:
                                bullet['alive'] = False
                        elif not bullet['penetrate']:
                            bullet['alive'] = False
        self.bullets = [b for b in self.bullets if b['alive']]
        # Sniper line damage
        if self.weapons[self.current_weapon]['name'] == 'Sniper' and self.is_firing and self.fire_line and enemies:
            x0, y0, x1, y1 = self.fire_line
            for enemy in enemies:
                if not enemy.alive:
                    continue
                ex, ey = enemy.x, enemy.y
                if self.line_intersects_rect(x0, y0, x1, y1, ex, ey, 16, 16):
                    enemy.take_damage(5)
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        # Clamp player x position to map walls
        map_walls = self.structure[level]["mapWall"]
        if len(map_walls) >= 2:
            left_wall = map_walls[0]
            right_wall = map_walls[1]
            min_x = left_wall[0] + left_wall[2]  # right edge of left wall
            max_x = right_wall[0] - 16           # left edge of right wall minus player width
            if self.x < min_x:
                self.x = min_x
            if self.x > max_x:
                self.x = max_x
        # Optionally clamp y to not fall below the map
        map_height = self.structure[level]["mapWH"][1]
        if self.y > map_height:
            self.y = map_height
            self.velocity_y = 0
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
        # Shield stamina and cooldown logic
        if pyxel.btn(pyxel.KEY_SHIFT) and self.shield_stamina > 0 and self.shield_cooldown == 0:
            self.is_shielding = True
            self.speed = self.shield_speed
            self.shield_stamina -= 1
            if self.shield_stamina <= 0:
                self.shield_stamina = 0
                self.is_shielding = False
                self.shield_cooldown = self.shield_cooldown_max
                self.speed = self.normal_speed
        else:
            if self.is_shielding:
                self.speed = self.normal_speed
            self.is_shielding = False
            if self.shield_cooldown > 0:
                self.shield_cooldown -= 1
            elif self.shield_stamina < self.shield_stamina_max:
                self.shield_stamina += 1

    def calculate_fire_line(self, angle, camera_x=0):
        # Start at gun muzzle
        player_cx = self.x + 8
        player_cy = self.y + 8
        muzzle_x = int(player_cx + math.cos(angle) * 8)
        muzzle_y = int(player_cy + math.sin(angle) * 8)
        # Step along the line until hit floor or map edge
        max_length = 2560  # Use map width instead of screen size
        step = 2
        for l in range(0, max_length, step):
            tx = int(muzzle_x + math.cos(angle) * l)
            ty = int(muzzle_y + math.sin(angle) * l)
            # Check map bounds (world coordinates)
            if tx < 0 or tx >= 2560 or ty < 0 or ty >= 128:
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

    def get_weapon_direction_index(self, camera_x=0):
        # 8 directions: [L, R, R45U, L45U, L45D, R45D, D, U]
        player_screen_x = self.x - camera_x + 8
        player_screen_y = self.y + 8
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        angle = math.degrees(math.atan2(my - player_screen_y, mx - player_screen_x))
        if angle < 0:
            angle += 360
        if 157.5 <= angle < 202.5:
            return 0  # Left
        elif angle < 22.5 or angle >= 337.5:
            return 1  # Right
        elif 22.5 <= angle < 67.5:
            return 5  # Right 45 Up
        elif 112.5 <= angle < 157.5:
            return 4  # Left 45 Up
        elif 202.5 <= angle < 247.5:
            return 3  # Left 45 Down
        elif 292.5 <= angle < 337.5:
            return 2  # Right 45 Down
        elif 247.5 <= angle < 292.5:
            return 7  # Down
        elif 67.5 <= angle < 112.5:
            return 6  # Up
        else:
            return 1  # Default to Right

    def draw_weapon(self, x_offset=0, camera_x=0):
        player_screen_x = self.x - x_offset + 8
        player_screen_y = self.y + 8
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        angle = math.atan2(my - player_screen_y, mx - player_screen_x)
        angle_deg = math.degrees(angle)
        idx = self.get_weapon_direction_index_from_angle(angle_deg)
        if self.is_firing:
            sx, sy = self.weapon_fire_sprites[idx]
        else:
            sx, sy = self.weapon_sprites[idx]
        wx = int(player_screen_x + math.cos(angle) * 8 - self.weapon_w // 2)
        wy = int(player_screen_y + math.sin(angle) * 8 - self.weapon_h // 2)
        pyxel.blt(wx, wy, 0, sx, sy, self.weapon_w, self.weapon_h, 14)
        if self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            pyxel.line(x0 - x_offset, y0, x1 - x_offset, y1, 8)

    def get_weapon_direction_index_from_angle(self, angle):
        if angle < 0:
            angle += 360
        if 157.5 <= angle < 202.5:
            return 0  # Left
        elif angle < 22.5 or angle >= 337.5:
            return 1  # Right
        elif 22.5 <= angle < 67.5:
            return 5  # Right 45 Up
        elif 112.5 <= angle < 157.5:
            return 4  # Left 45 Up
        elif 202.5 <= angle < 247.5:
            return 3  # Left 45 Down
        elif 292.5 <= angle < 337.5:
            return 2  # Right 45 Down
        elif 247.5 <= angle < 292.5:
            return 7  # Down
        elif 67.5 <= angle < 112.5:
            return 6  # Up
        else:
            return 1  # Default to Right

    def draw(self, x_offset=0, camera_x=0):
        # Draw player sprite
        if self.is_moving:
            # Draw walking animation
            if self.facing_direction == 1:  # Right
                frame = self.walk_right[self.animation_frame]
            else:  # Left
                frame = self.walk_left[self.animation_frame]
            pyxel.blt(self.x - x_offset, self.y, 0, frame[0], frame[1], 16, 16, 14)
        else:
            # Draw standing frame based on facing direction
            if self.facing_direction == 1:  # Right
                pyxel.blt(self.x - x_offset, self.y, 0, self.stand_frame_right[0], self.stand_frame_right[1], 16, 16, 14)
            else:  # Left
                pyxel.blt(self.x - x_offset, self.y, 0, self.stand_frame_left[0], self.stand_frame_left[1], 16, 16, 14)
        # Draw shield overlay if shielding
        if self.is_shielding:
            if self.facing_direction == 1:  # Right
                pyxel.blt(self.x - x_offset + 4, self.y, 0, 32, 144, 16, 16, 14)
            else:  # Left
                pyxel.blt(self.x - x_offset - 4, self.y, 0, 48, 144, 16, 16, 14)
        # Draw weapon after player
        self.draw_weapon(x_offset, camera_x)
        # Draw health bar above player (red)
        bar_x = self.x - x_offset
        bar_y = self.y - 8
        bar_w = 16
        bar_h = 2
        health_ratio = self.health / self.max_health
        pyxel.rect(bar_x, bar_y, int(bar_w * health_ratio), bar_h, 8)
        # Draw player health text
        pyxel.text(5, 5, f"HP: {self.health}/{self.max_health}", 7)
        # Draw shield icon and bar at bottom left
        icon_x = 2
        icon_y = pyxel.height - 12
        pyxel.blt(icon_x, icon_y, 0, 0, 192, 8, 8, 0)
        # Draw shield stamina/cooldown bar below icon
        bar_x = icon_x
        bar_y = icon_y + 9
        bar_w = 8
        bar_h = 2
        stamina_ratio = self.shield_stamina / self.shield_stamina_max
        pyxel.rect(bar_x, bar_y, int(bar_w * stamina_ratio), bar_h, 11)
        if self.shield_cooldown > 0:
            cd_ratio = self.shield_cooldown / self.shield_cooldown_max
            pyxel.rect(bar_x, bar_y, int(bar_w * cd_ratio), bar_h, 8)
        # Draw bullets
        for bullet in self.bullets:
            if bullet['alive']:
                pyxel.circ(bullet['x'] - x_offset, bullet['y'], 1, bullet['color'])
        # Draw sniper line if active
        if self.weapons[self.current_weapon]['name'] == 'Sniper' and self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            pyxel.line(x0 - x_offset, y0, x1 - x_offset, y1, 8)

    @staticmethod
    def line_intersects_rect(x0, y0, x1, y1, rx, ry, rw, rh):
        # Simple AABB vs line segment check
        if rx <= x0 <= rx+rw and ry <= y0 <= ry+rh:
            return True
        if rx <= x1 <= rx+rw and ry <= y1 <= ry+rh:
            return True
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        def intersect(A,B,C,D):
            return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
        rect_edges = [
            ((rx,ry), (rx+rw,ry)),
            ((rx+rw,ry), (rx+rw,ry+rh)),
            ((rx+rw,ry+rh), (rx,ry+rh)),
            ((rx,ry+rh), (rx,ry)),
        ]
        for edge in rect_edges:
            if intersect((x0,y0), (x1,y1), edge[0], edge[1]):
                return True
        return False

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False