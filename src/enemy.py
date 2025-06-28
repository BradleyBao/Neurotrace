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
        # Weapon system (weapon_sprites will be set in subclasses)
        self.weapon_offset = 5
        self.weapon_w = 8
        self.weapon_h = 8
        self.is_firing = False
        self.fire_timer = 0
        self.fire_duration = 24
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
        self.weapon = "Basic Gun"  # Placeholder, override in subclasses
        self.special_ability = None  # Placeholder, override in subclasses
        # Default sprite locations (can be overridden in subclasses)
        self.sprite_left = (0, 0)
        self.sprite_right = (16, 0)
        self.sprite_damage_left = (32, 0)
        self.sprite_damage_right = (48, 0)
        self.sprite_defeated_left = (64, 0)
        self.sprite_defeated_right = (80, 0)
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
        if self.state == "patrol":
            if distance_to_player < 80:
                self.state = "chase"
            elif self.stand_timer > 0:
                self.is_moving = False
                self.stand_timer -= 1
            else:
                self.is_moving = True
                self.x += self.speed * self.patrol_dir
                self.facing_direction = self.patrol_dir
                if abs(self.x - self.patrol_origin) > self.patrol_range:
                    self.patrol_dir *= -1
                    self.stand_timer = random.randint(30, 90)
        elif self.state == "chase":
            if distance_to_player < 40:
                self.state = "retreat"
                self.retreat_timer = random.randint(30, 60)
            elif distance_to_player < 60:
                self.state = "attack"
            elif distance_to_player > 100:
                self.state = "patrol"
            else:
                self.is_moving = True
                if player.x > self.x:
                    self.x += self.speed
                    self.facing_direction = 1
                elif player.x < self.x:
                    self.x -= self.speed
                    self.facing_direction = -1
        elif self.state == "attack":
            if distance_to_player < 40:
                self.state = "retreat"
                self.retreat_timer = random.randint(30, 60)
            elif distance_to_player > 80:
                self.state = "chase"
            else:
                self.is_moving = False
                self.facing_direction = 1 if player.x > self.x else -1
                if self.attack_cooldown == 0:
                    self.fire(player, camera_x)
                    self.attack_cooldown = self.attack_cooldown_max
        elif self.state == "retreat":
            if self.retreat_timer > 0:
                self.is_moving = True
                if player.x > self.x:
                    self.x -= self.speed
                    self.facing_direction = -1
                else:
                    self.x += self.speed
                    self.facing_direction = 1
                self.retreat_timer -= 1
            else:
                self.state = "patrol"
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.checkFloorCollision(self.level)
        if self.is_firing:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.is_firing = False
                self.fire_line = None
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def fire(self, player, camera_x=0):
        if not self.is_firing:
            self.is_firing = True
            self.fire_timer = self.fire_duration
            enemy_screen_x = self.x - camera_x + 8
            enemy_screen_y = self.y + 8
            player_screen_x = player.x - camera_x + 8
            player_screen_y = player.y + 8
            angle = math.atan2(player_screen_y - enemy_screen_y, player_screen_x - enemy_screen_x)
            if random.random() < self.miss_chance:
                angle += random.uniform(-0.4, 0.4)
            self.fire_angle = angle
            self.fire_line = self.calculate_fire_line(self.fire_angle)

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
        if self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            pyxel.line(x0 - x_offset, y0, x1 - x_offset, y1, 8)

# Robot Enemies
class RobotEnemy0(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(0, x, y, level)
        self.miss_chance = 0.75
        self.weapon = "Laser Blaster"
        self.special_ability = "Shield (placeholder)"
        self.hp = 20
        self.sprite_left = (0, 16)
        self.sprite_right = (16, 16)
        self.sprite_damage_left = (32, 16)
        self.sprite_damage_right = (48, 16)
        self.sprite_defeated_left = (64, 16)
        self.sprite_defeated_right = (80, 16)
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
class RobotEnemy1(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(1, x, y, level)
        self.miss_chance = 0.7
        self.weapon = "Pulse Rifle"
        self.special_ability = "EMP (placeholder)"
        self.hp = 18
        self.sprite_left = (0, 96)
        self.sprite_right = (16, 96)
        self.sprite_damage_left = (32, 96)
        self.sprite_damage_right = (48, 96)
        self.sprite_defeated_left = (64, 96)
        self.sprite_defeated_right = (80, 96)
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
class RobotEnemy2(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(2, x, y, level)
        self.miss_chance = 0.4
        self.weapon = "Rocket Arm"
        self.special_ability = "Rocket Jump (placeholder)"
        self.hp = 25
        self.sprite_left = (0, 112)
        self.sprite_right = (16, 112)
        self.sprite_damage_left = (32, 112)
        self.sprite_damage_right = (48, 112)
        self.sprite_defeated_left = (64, 112)
        self.sprite_defeated_right = (80, 112)
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
# Human Enemies
class HumanEnemy0(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(3, x, y, level)
        self.miss_chance = 0.8
        self.weapon = "Pistol"
        self.special_ability = "Roll (placeholder)"
        self.hp = 8
        self.sprite_left = (0, 32)
        self.sprite_right = (16, 32)
        self.sprite_damage_left = (32, 32)
        self.sprite_damage_right = (48, 32)
        self.sprite_defeated_left = (64, 32)
        self.sprite_defeated_right = (80, 32)
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
class HumanEnemy1(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(4, x, y, level)
        self.miss_chance = 0.6
        self.weapon = "Shotgun"
        self.special_ability = "Sprint (placeholder)"
        self.hp = 10
        self.sprite_left = (0, 46)
        self.sprite_right = (16, 46)
        self.sprite_damage_left = (32, 46)
        self.sprite_damage_right = (48, 46)
        self.sprite_defeated_left = (64, 46)
        self.sprite_defeated_right = (80, 46)
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
class HumanEnemy2(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(5, x, y, level)
        self.miss_chance = 0.3
        self.weapon = "SMG"
        self.special_ability = "Grenade (placeholder)"
        self.hp = 12
        self.sprite_left = (0, 64)
        self.sprite_right = (16, 64)
        self.sprite_damage_left = (32, 64)
        self.sprite_damage_right = (48, 64)
        self.sprite_defeated_left = (64, 64)
        self.sprite_defeated_right = (80, 64)
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
class HumanEnemy3(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(6, x, y, level)
        self.miss_chance = 0.1
        self.weapon = "Sniper"
        self.special_ability = "Camouflage (placeholder)"
        self.hp = 6
        self.sprite_left = (0, 80)
        self.sprite_right = (16, 80)
        self.sprite_damage_left = (32, 80)
        self.sprite_damage_right = (48, 80)
        self.sprite_defeated_left = (64, 80)
        self.sprite_defeated_right = (80, 80)
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