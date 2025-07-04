import pyxel
import src.settings
import src.structure
import math
import random

class BaseEnemy:
    def __init__(self, type_index, x, y, level=0):
        self.type_index = type_index
        self.x = x
        self.y = y
        self.level = level
        self.structure = src.structure.STRUCTURE
        self.speed = src.settings.PLAYER_SPEED * 0.8
        self.jump_speed = src.settings.PLAYER_JUMP_SPEED
        self.gravity = src.settings.GRAVITY
        self.velocity_y = 0
        self.is_jumping = False
        self.is_moving = False
        self.facing_direction = 1
        self.animation_frame = 0
        self.animation_timer = 0
        # Weapon system
        self.weapon_types = [
            {
                'name': 'Pistol',
                'sprites': [
                    (0, 128), (8, 128), (0, 136), (8, 136), (16, 128), (24, 128), (16, 136), (24, 136)
                ],
                'range': 60,
                'ai': 'default',
            },
            {
                'name': 'Rifle',
                'sprites': [
                    (0, 160), (8, 160), (0, 168), (8, 168), (16, 160), (24, 160), (16, 168), (24, 168)
                ],
                'range': 100,
                'ai': 'rifle',
            },
            {
                'name': 'Sniper',
                'sprites': [
                    (0, 176), (8, 176), (0, 184), (8, 184), (16, 176), (24, 176), (16, 184), (24, 184)
                ],
                'range': 180,
                'ai': 'sniper',
            },
        ]
        weapon_choice = random.choice(self.weapon_types)
        self.weapon = weapon_choice['name']
        self.weapon_sprites = weapon_choice['sprites']
        self.weapon_range = weapon_choice['range']
        self.weapon_ai = weapon_choice['ai']
        # Weapon system (weapon_sprites will be set in subclasses)
        self.weapon_offset = 5
        self.weapon_w = 8
        self.weapon_h = 8
        self.is_firing = False
        self.fire_timer = 0
        self.fire_duration = 6
        self.fire_angle = 0
        self.fire_line = None
        # AI State
        self.visual_state = "normal"  # normal, damage, defeated
        self.visual_state_timer = 0
        self.state = "patrol"  # AI state: patrol, chase, attack, retreat
        self.alive = True
        self.hp = 10  # Default, override in subclasses
        self.patrol_origin = x
        self.patrol_range = 32 + random.randint(0, 32)
        self.patrol_dir = 1 if random.random() < 0.5 else -1
        self.stand_timer = 0
        self.retreat_timer = 0
        # Attack cooldown and miss chance
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60
        self.miss_chance = 0.2  # Default, override in subclasses
        self.special_ability = None  # Placeholder, override in subclasses
        # Default sprite locations (can be overridden in subclasses)
        self.sprite_left = (0, 0)
        self.sprite_right = (16, 0)
        self.sprite_damage_left = (32, 0)
        self.sprite_damage_right = (48, 0)
        self.sprite_defeated_left = (64, 0)
        self.sprite_defeated_right = (80, 0)
        self.bullets = []  # List of bullets: {'x', 'y', 'vx', 'vy', 'color', 'penetrate', 'alive'}

    def take_damage(self, amount):
        if self.visual_state == "defeated":
            return
        self.hp -= amount
        if self.hp <= 0:
            self.visual_state = "defeated"
            self.alive = False
        else:
            self.visual_state = "damage"
            self.visual_state_timer = 10  # Show damage sprite for 10 frames

    def update(self, player, camera_x=0):
        if self.visual_state == "damage":
            self.visual_state_timer -= 1
            if self.visual_state_timer <= 0 and self.hp > 0:
                self.visual_state = "normal"
        if self.visual_state == "defeated":
            return
        if not self.alive:
            return
        distance_to_player = abs(player.x - self.x)
        # Smarter AI: check for platform edge before moving
        def will_fall_off_platform(dx):
            next_x = self.x + dx
            for floor in self.structure[self.level]["mapFloor"]:
                fx, fy, fw, fh = floor
                if fx <= next_x < fx+fw and self.y+16 == fy:
                    return False
            return True
        # Weapon-based AI thresholds
        if self.weapon_ai == 'sniper':
            retreat_dist = 120
            attack_min = 120
            attack_max = self.weapon_range
            patrol_dist = 200
        elif self.weapon_ai == 'rifle':
            retreat_dist = 40
            attack_min = 40
            attack_max = self.weapon_range
            patrol_dist = 120
        else:
            retreat_dist = 40
            attack_min = 40
            attack_max = 60
            patrol_dist = 100
        # State machine for all weapons
        if self.state == 'patrol':
            if distance_to_player < attack_max:
                self.state = 'chase'
            elif self.stand_timer > 0:
                self.is_moving = False
                self.stand_timer -= 1
            else:
                self.is_moving = True
                dx = self.speed * self.patrol_dir
                if not will_fall_off_platform(dx):
                    self.x += dx
                    self.facing_direction = self.patrol_dir
                if abs(self.x - self.patrol_origin) > self.patrol_range:
                    self.patrol_dir *= -1
                    self.stand_timer = random.randint(30, 90)
        elif self.state == 'chase':
            if distance_to_player < retreat_dist:
                self.state = 'retreat'
                self.retreat_timer = random.randint(30, 60)
            elif attack_min <= distance_to_player < attack_max:
                self.state = 'attack'
            elif distance_to_player > patrol_dist:
                self.state = 'patrol'
            else:
                self.is_moving = True
                dx = self.speed if player.x > self.x else -self.speed
                if not will_fall_off_platform(dx):
                    self.x += dx
                    self.facing_direction = 1 if player.x > self.x else -1
        elif self.state == 'attack':
            if distance_to_player < retreat_dist:
                self.state = 'retreat'
                self.retreat_timer = random.randint(30, 60)
            elif distance_to_player > attack_max:
                self.state = 'chase'
            else:
                self.is_moving = False
                self.facing_direction = 1 if player.x > self.x else -1
                if self.attack_cooldown == 0:
                    self.fire(player, camera_x)
                    self.attack_cooldown = self.attack_cooldown_max
        elif self.state == 'retreat':
            if self.retreat_timer > 0:
                self.is_moving = True
                dx = -self.speed if player.x > self.x else self.speed
                if not will_fall_off_platform(dx):
                    self.x += dx
                    self.facing_direction = -1 if player.x > self.x else 1
                self.retreat_timer -= 1
            else:
                self.state = 'patrol'
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        # Clamp enemy x position to map walls
        map_walls = self.structure[self.level]["mapWall"]
        if len(map_walls) >= 2:
            left_wall = map_walls[0]
            right_wall = map_walls[1]
            min_x = left_wall[0] + left_wall[2]
            max_x = right_wall[0] - 16
            if self.x < min_x:
                self.x = min_x
            if self.x > max_x:
                self.x = max_x
        # Clamp y to not fall below map
        map_height = self.structure[self.level]["mapWH"][1]
        if self.y > map_height:
            self.y = map_height
            self.velocity_y = 0
        self.checkFloorCollision(self.level)
        if self.is_firing:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.is_firing = False
                self.fire_line = None
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
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
            for floor in self.structure[self.level]['mapFloor']:
                fx, fy, fw, fh = floor
                if fx <= bullet['x'] <= fx+fw and fy <= bullet['y'] <= fy+fh:
                    bullet['alive'] = False
            # Bullet collision with map walls
            for wall in self.structure[self.level]['mapWall']:
                wx, wy, ww, wh = wall
                if wx <= bullet['x'] <= wx+ww and wy <= bullet['y'] <= wy+wh:
                    bullet['alive'] = False
            # Bullet collision with player
            if (player.x < bullet['x'] < player.x+16 and player.y < bullet['y'] < player.y+16):
                if self.weapon == 'Pistol':
                    player.take_damage(1)
                elif self.weapon == 'Rifle':
                    player.take_damage(2)
                    if bullet.get('penetrate_count') is not None:
                        bullet['penetrate_count'] -= 1
                        if bullet['penetrate_count'] <= 0:
                            bullet['alive'] = False
                if not bullet['penetrate']:
                    bullet['alive'] = False
        self.bullets = [b for b in self.bullets if b['alive']]
        # Sniper line damage
        if self.weapon == 'Sniper' and self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            if self.line_intersects_rect(x0, y0, x1, y1, player.x, player.y, 16, 16):
                player.take_damage(5)

    def fire(self, player, camera_x=0):
        if not self.is_firing:
            self.is_firing = True
            self.fire_timer = self.fire_duration
            enemy_screen_x = self.x - camera_x + 8
            enemy_screen_y = self.y + 8
            player_screen_x = player.x - camera_x + 8
            player_screen_y = player.y + 8
            # Lead shot: predict player position
            player_vx = getattr(player, 'velocity_x', 0) if hasattr(player, 'velocity_x') else 0
            lead_time = 8 / max(1, abs(player_vx)) if player_vx != 0 else 0
            predicted_x = player.x + player_vx * lead_time
            angle = math.atan2(player_screen_y - enemy_screen_y, predicted_x - self.x)
            if random.random() < self.miss_chance:
                angle += random.uniform(-0.4, 0.4)
            if self.weapon == 'Sniper':
                self.fire_angle = angle
                self.fire_line = self.calculate_fire_line(angle)
            else:
                speed = 8 if self.weapon == 'Rifle' else 5
                color = 12 if self.weapon == 'Rifle' else 0
                penetrate = True if self.weapon == 'Rifle' else False
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                bx = self.x + 8 + vx * 2
                by = self.y + 8 + vy * 2
                bullet = {'x': bx, 'y': by, 'vx': vx, 'vy': vy, 'color': color, 'penetrate': penetrate, 'alive': True}
                if self.weapon == 'Rifle':
                    bullet['penetrate_count'] = 2
                self.bullets.append(bullet)

    def calculate_fire_line(self, angle):
        enemy_cx = self.x + 8
        enemy_cy = self.y + 8
        muzzle_x = int(enemy_cx + math.cos(angle) * 8)
        muzzle_y = int(enemy_cy + math.sin(angle) * 8)
        max_length = 2560
        step = 2
        for l in range(0, max_length, step):
            tx = int(muzzle_x + math.cos(angle) * l)
            ty = int(muzzle_y + math.sin(angle) * l)
            if tx < 0 or tx >= 2560 or ty < 0 or ty >= 128:
                return (muzzle_x, muzzle_y, tx, ty)
            for floor in self.structure[self.level]["mapFloor"]:
                fx, fy, fw, fh = floor
                if fx <= tx < fx+fw and fy <= ty < fy+fh:
                    return (muzzle_x, muzzle_y, tx, ty)
        tx = int(muzzle_x + math.cos(angle) * max_length)
        ty = int(muzzle_y + math.sin(angle) * max_length)
        return (muzzle_x, muzzle_y, tx, ty)

    def checkFloorCollision(self, level):
        floors = self.structure[level]["mapFloor"]
        on_floor = False
        for floor in floors:
            floor_x, floor_y, floor_w, floor_h = floor
            if (self.x < floor_x + floor_w and 
                self.x + 16 > floor_x and 
                self.y + 16 >= floor_y and 
                self.y + 16 <= floor_y + floor_h + 5):
                self.y = floor_y - 16
                self.velocity_y = 0
                self.is_jumping = False
                on_floor = True
                break
        if not on_floor:
            self.is_jumping = True

    def draw(self, x_offset=0, target=None):
        if self.visual_state == "defeated":
            sx, sy = self.sprite_defeated_right if self.facing_direction == 1 else self.sprite_defeated_left
        elif self.visual_state == "damage":
            sx, sy = self.sprite_damage_right if self.facing_direction == 1 else self.sprite_damage_left
        else:
            sx, sy = self.sprite_right if self.facing_direction == 1 else self.sprite_left
        pyxel.blt(self.x - x_offset, self.y, 0, sx, sy, 16, 16, 14)
        if self.visual_state != "defeated":
            self.draw_weapon(x_offset, target)
        # Draw bullets
        for bullet in self.bullets:
            if bullet['alive']:
                pyxel.circ(bullet['x'] - x_offset, bullet['y'], 1, bullet['color'])
        # Draw sniper line if active
        if self.weapon == 'Sniper' and self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            pyxel.line(x0 - x_offset, y0, x1 - x_offset, y1, 8)

    def draw_weapon(self, x_offset=0, target=None):
        # Use player weapon logic for aiming and facing
        if target is not None:
            enemy_screen_x = self.x - x_offset + 8
            enemy_screen_y = self.y + 8
            player_screen_x = target.x - x_offset + 8
            player_screen_y = target.y + 8
            angle = math.atan2(player_screen_y - enemy_screen_y, player_screen_x - enemy_screen_x)
        else:
            angle = 0
        angle_deg = math.degrees(angle)
        if angle_deg < 0:
            angle_deg += 360
        if 157.5 <= angle_deg < 202.5:
            idx = 0  # Left
        elif angle_deg < 22.5 or angle_deg >= 337.5:
            idx = 1  # Right
        elif 22.5 <= angle_deg < 67.5:
            idx = 5  # Right 45 Up
        elif 112.5 <= angle_deg < 157.5:
            idx = 4  # Left 45 Up
        elif 202.5 <= angle_deg < 247.5:
            idx = 3  # Left 45 Down
        elif 292.5 <= angle_deg < 337.5:
            idx = 2  # Right 45 Down
        elif 247.5 <= angle_deg < 292.5:
            idx = 7  # Down
        elif 67.5 <= angle_deg < 112.5:
            idx = 6  # Up
        else:
            idx = 1  # Default to Right
        sx, sy = self.weapon_sprites[idx]
        enemy_screen_x = self.x - x_offset + 8
        enemy_screen_y = self.y + 8
        wx = int(enemy_screen_x + math.cos(angle) * 8 - self.weapon_w // 2)
        wy = int(enemy_screen_y + math.sin(angle) * 8 - self.weapon_h // 2)
        pyxel.blt(wx, wy, 0, sx, sy, self.weapon_w, self.weapon_h, 14)

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

# Robot Enemies
class RobotEnemy0(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(0, x, y, level)
        self.miss_chance = 0.75
        self.special_ability = "Shield (placeholder)"
        self.hp = 30
        self.sprite_left = (0, 16)
        self.sprite_right = (16, 16)
        self.sprite_damage_left = (32, 16)
        self.sprite_damage_right = (48, 16)
        self.sprite_defeated_left = (64, 16)
        self.sprite_defeated_right = (80, 16)
class RobotEnemy1(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(1, x, y, level)
        self.miss_chance = 0.7
        self.special_ability = "EMP (placeholder)"
        self.hp = 35
        self.sprite_left = (0, 96)
        self.sprite_right = (16, 96)
        self.sprite_damage_left = (32, 96)
        self.sprite_damage_right = (48, 96)
        self.sprite_defeated_left = (64, 96)
        self.sprite_defeated_right = (80, 96)
class RobotEnemy2(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(2, x, y, level)
        self.miss_chance = 0.4
        self.special_ability = "Rocket Jump (placeholder)"
        self.hp = 45
        self.sprite_left = (0, 112)
        self.sprite_right = (16, 112)
        self.sprite_damage_left = (32, 112)
        self.sprite_damage_right = (48, 112)
        self.sprite_defeated_left = (64, 112)
        self.sprite_defeated_right = (80, 112)
# Human Enemies
class HumanEnemy0(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(3, x, y, level)
        self.miss_chance = 0.8
        self.special_ability = "Roll (placeholder)"
        self.hp = 20
        self.sprite_left = (0, 32)
        self.sprite_right = (16, 32)
        self.sprite_damage_left = (32, 32)
        self.sprite_damage_right = (48, 32)
        self.sprite_defeated_left = (64, 32)
        self.sprite_defeated_right = (80, 32)
class HumanEnemy1(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(4, x, y, level)
        self.miss_chance = 0.6
        self.special_ability = "Sprint (placeholder)"
        self.hp = 25
        self.sprite_left = (0, 48)
        self.sprite_right = (16, 48)
        self.sprite_damage_left = (32, 48)
        self.sprite_damage_right = (48, 48)
        self.sprite_defeated_left = (64, 48)
        self.sprite_defeated_right = (80, 48)
class HumanEnemy2(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(5, x, y, level)
        self.miss_chance = 0.3
        self.special_ability = "Grenade (placeholder)"
        self.hp = 35
        self.sprite_left = (0, 64)
        self.sprite_right = (16, 64)
        self.sprite_damage_left = (32, 64)
        self.sprite_damage_right = (48, 64)
        self.sprite_defeated_left = (64, 64)
        self.sprite_defeated_right = (80, 64)
class HumanEnemy3(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(6, x, y, level)
        self.miss_chance = 0.1
        self.special_ability = "Camouflage (placeholder)"
        self.hp = 50
        self.sprite_left = (0, 80)
        self.sprite_right = (16, 80)
        self.sprite_damage_left = (32, 80)
        self.sprite_damage_right = (48, 80)
        self.sprite_defeated_left = (64, 80)
        self.sprite_defeated_right = (80, 80)

def create_enemy(type_index, x, y, level=0):
    if type_index == 0:
        return RobotEnemy0(x, y, level)
    elif type_index == 1:
        return RobotEnemy1(x, y, level)
    elif type_index == 2:
        return RobotEnemy2(x, y, level)
    elif type_index == 3:
        return HumanEnemy0(x, y, level)
    elif type_index == 4:
        return HumanEnemy1(x, y, level)
    elif type_index == 5:
        return HumanEnemy2(x, y, level)
    elif type_index == 6:
        return HumanEnemy3(x, y, level)
    else:
        return BaseEnemy(type_index, x, y, level) 