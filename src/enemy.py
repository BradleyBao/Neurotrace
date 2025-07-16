import pyxel
import src.settings
import src.structure
import math
import random
# from src.enemy import create_enemy

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
        # Special ability system
        self.special_ability = None  # Placeholder, override in subclasses
        self.special_cooldown = 0
        self.special_cooldown_max = 120  # Default, override in subclasses
        self.special_active = False
        self.special_timer = 0
        self.special_duration = 60  # Default, override in subclasses
        # Default sprite locations (can be overridden in subclasses)
        self.sprite_left = (0, 0)
        self.sprite_right = (16, 0)
        self.sprite_damage_left = (32, 0)
        self.sprite_damage_right = (48, 0)
        self.sprite_defeated_left = (64, 0)
        self.sprite_defeated_right = (80, 0)
        self.bullets = []  # List of bullets: {'x', 'y', 'vx', 'vy', 'color', 'penetrate', 'alive'}
        # Grenade system
        self.grenades = []  # List of grenades: {'x', 'y', 'vx', 'vy', 'timer', 'alive', 'exploded'}

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

    def use_special_ability(self, player):
        """Use special ability if cooldown is ready"""
        if self.special_cooldown <= 0 and not self.special_active:
            self.special_cooldown = self.special_cooldown_max
            self.special_active = True
            self.special_timer = self.special_duration
            self.activate_special_ability(player)

    def activate_special_ability(self, player):
        """Override in subclasses to implement specific abilities"""
        pass

    def update_special_ability(self, player):
        """Update special ability effects"""
        if self.special_active:
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.special_active = False
                self.deactivate_special_ability(player)
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

    def deactivate_special_ability(self, player):
        """Override in subclasses to clean up ability effects"""
        pass

    def draw_special_effect(self, x_offset):
        """Override in subclasses to draw special ability effects"""
        pass

    def throw_grenade(self, target_x, target_y):
        """Throw a grenade towards target position"""
        if self.special_cooldown <= 0:
            # Calculate trajectory
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Normalize direction
            if distance > 0:
                dx /= distance
                dy /= distance
            
            # Add some randomness and arc
            speed = 2.0 + random.uniform(-0.5, 0.5)
            vx = dx * speed
            vy = dy * speed - 1.0  # Add upward arc
            
            grenade = {
                'x': self.x + 8,
                'y': self.y + 8,
                'vx': vx,
                'vy': vy,
                'timer': 120,  # 2 seconds at 60fps
                'alive': True,
                'exploded': False
            }
            self.grenades.append(grenade)
            self.special_cooldown = self.special_cooldown_max

    def update_grenades(self, player):
        """Update grenade physics and explosion"""
        for grenade in self.grenades[:]:
            if not grenade['alive']:
                continue
                
            # Update position
            grenade['x'] += grenade['vx']
            grenade['y'] += grenade['vy']
            grenade['vy'] += 0.1  # Gravity
            
            # Update timer
            grenade['timer'] -= 1
            
            # Check for explosion
            if grenade['timer'] <= 0 or grenade['y'] > 128:  # Hit ground or timer expired
                grenade['exploded'] = True
                grenade['alive'] = False
                
                # Check if player is in explosion radius
                explosion_radius = 24
                dx = grenade['x'] - (player.x + 8)
                dy = grenade['y'] - (player.y + 8)
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= explosion_radius:
                    player.take_damage(3)  # Grenade damage

    def update(self, player, camera_x=0):
        if self.visual_state == "damage":
            self.visual_state_timer -= 1
            if self.visual_state_timer <= 0 and self.hp > 0:
                self.visual_state = "normal"
        if self.visual_state == "defeated":
            return
        if not self.alive:
            return
            
        # Update special ability
        self.update_special_ability(player)
        
        # Update grenades
        self.update_grenades(player)
        
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
                # Try to use special ability during attack
                if random.random() < 0.1:  # 10% chance per frame during attack
                    self.use_special_ability(player)
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
        
        # Draw grenades
        for grenade in self.grenades:
            if grenade['alive']:
                pyxel.blt(grenade['x'] - x_offset - 4, grenade['y'] - 4, 0, 0, 208, 8, 8, 0)
        
        # Draw special ability effects
        if self.special_active:
            self.draw_special_effect(x_offset)

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
        self.special_ability = "Shield"
        self.special_cooldown_max = 180  # 3 seconds
        self.special_duration = 120  # 2 seconds
        self.hp = 30
        self.sprite_left = (0, 16)
        self.sprite_right = (16, 16)
        self.sprite_damage_left = (32, 16)
        self.sprite_damage_right = (48, 16)
        self.sprite_defeated_left = (64, 16)
        self.sprite_defeated_right = (80, 16)
        self.original_speed = self.speed

    def activate_special_ability(self, player):
        """Activate shield - reduces damage taken and slows movement"""
        self.speed = self.original_speed * 0.5  # Slow down while shielded

    def deactivate_special_ability(self, player):
        """Deactivate shield"""
        self.speed = self.original_speed

    def take_damage(self, amount):
        """Override to reduce damage when shield is active"""
        if self.special_active:
            amount = max(1, amount // 3)  # Reduce damage by 2/3 when shielded
        super().take_damage(amount)

    def draw_special_effect(self, x_offset):
        """Draw shield effect"""
        if self.special_active:
            # Draw shield overlay
            if self.facing_direction == 1:  # Right
                pyxel.blt(self.x - x_offset + 4, self.y, 0, 32, 144, 16, 16, 14)
            else:  # Left
                pyxel.blt(self.x - x_offset - 4, self.y, 0, 48, 144, 16, 16, 14)
class RobotEnemy1(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(1, x, y, level)
        self.miss_chance = 0.7
        self.special_ability = "EMP"
        self.special_cooldown_max = 300  # 5 seconds
        self.special_duration = 90  # 1.5 seconds
        self.hp = 35
        self.sprite_left = (0, 96)
        self.sprite_right = (16, 96)
        self.sprite_damage_left = (32, 96)
        self.sprite_damage_right = (48, 96)
        self.sprite_defeated_left = (64, 96)
        self.sprite_defeated_right = (80, 96)
        self.emp_pulse_timer = 0

    def activate_special_ability(self, player):
        """Activate EMP - creates an electromagnetic pulse that damages player"""
        self.emp_pulse_timer = 30  # Create initial pulse

    def update_special_ability(self, player):
        """Update EMP effects"""
        super().update_special_ability(player)
        if self.emp_pulse_timer > 0:
            self.emp_pulse_timer -= 1
            # Check if player is in EMP range
            distance = abs(player.x - self.x)
            if distance <= 48:  # EMP range
                player.take_damage(1)  # Continuous damage during pulse

    def draw_special_effect(self, x_offset):
        """Draw EMP effect"""
        if self.special_active:
            # Draw EMP pulse
            pulse_radius = 48 - (self.special_timer // 2)
            if pulse_radius > 0:
                # Draw expanding circle effect
                for i in range(0, pulse_radius, 8):
                    alpha = max(0, 15 - (i // 4))
                    pyxel.circb(self.x - x_offset + 8, self.y + 8, i, alpha)
class RobotEnemy2(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(2, x, y, level)
        self.miss_chance = 0.4
        self.special_ability = "Rocket Jump"
        self.special_cooldown_max = 240  # 4 seconds
        self.special_duration = 30  # 0.5 seconds
        self.hp = 45
        self.sprite_left = (0, 112)
        self.sprite_right = (16, 112)
        self.sprite_damage_left = (32, 112)
        self.sprite_damage_right = (48, 112)
        self.sprite_defeated_left = (64, 112)
        self.sprite_defeated_right = (80, 112)
        self.rocket_jump_direction = 0

    def activate_special_ability(self, player):
        """Activate rocket jump - propels enemy upward and towards player"""
        # Calculate jump direction towards player
        if player.x > self.x:
            self.rocket_jump_direction = 1
        else:
            self.rocket_jump_direction = -1
        # Apply rocket jump force
        self.velocity_y = -8  # Strong upward force
        self.x += self.rocket_jump_direction * 16  # Horizontal boost

    def draw_special_effect(self, x_offset):
        """Draw rocket jump effect"""
        if self.special_active:
            # Draw rocket trail
            trail_x = self.x - x_offset + 8
            trail_y = self.y + 16
            for i in range(3):
                pyxel.pset(trail_x + random.randint(-2, 2), trail_y + i, 8)
# Human Enemies
class HumanEnemy0(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(3, x, y, level)
        self.miss_chance = 0.8
        self.special_ability = "Roll"
        self.special_cooldown_max = 120  # 2 seconds
        self.special_duration = 45  # 0.75 seconds
        self.hp = 20
        self.sprite_left = (0, 32)
        self.sprite_right = (16, 32)
        self.sprite_damage_left = (32, 32)
        self.sprite_damage_right = (48, 32)
        self.sprite_defeated_left = (64, 32)
        self.sprite_defeated_right = (80, 32)
        self.original_speed = self.speed
        self.roll_direction = 0

    def activate_special_ability(self, player):
        """Activate roll - quick dodge movement"""
        self.speed = self.original_speed * 2.5  # Fast roll speed
        # Roll away from player
        if player.x > self.x:
            self.roll_direction = -1
        else:
            self.roll_direction = 1
        self.facing_direction = self.roll_direction

    def deactivate_special_ability(self, player):
        """Deactivate roll"""
        self.speed = self.original_speed

    def update_special_ability(self, player):
        """Update roll movement"""
        super().update_special_ability(player)
        if self.special_active:
            # Move in roll direction
            self.x += self.roll_direction * self.speed

    def draw_special_effect(self, x_offset):
        """Draw roll effect"""
        if self.special_active:
            # Draw roll dust trail
            trail_x = self.x - x_offset + 8
            trail_y = self.y + 12
            for i in range(2):
                pyxel.pset(trail_x + random.randint(-3, 3), trail_y + i, 7)
class HumanEnemy1(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(4, x, y, level)
        self.miss_chance = 0.6
        self.special_ability = "Sprint"
        self.special_cooldown_max = 180  # 3 seconds
        self.special_duration = 90  # 1.5 seconds
        self.hp = 25
        self.sprite_left = (0, 48)
        self.sprite_right = (16, 48)
        self.sprite_damage_left = (32, 48)
        self.sprite_damage_right = (48, 48)
        self.sprite_defeated_left = (64, 48)
        self.sprite_defeated_right = (80, 48)
        self.original_speed = self.speed

    def activate_special_ability(self, player):
        """Activate sprint - increased movement speed"""
        self.speed = self.original_speed * 2.0  # Double speed

    def deactivate_special_ability(self, player):
        """Deactivate sprint"""
        self.speed = self.original_speed

    def draw_special_effect(self, x_offset):
        """Draw sprint effect"""
        if self.special_active:
            # Draw speed lines
            for i in range(3):
                line_x = self.x - x_offset + random.randint(0, 16)
                line_y = self.y + random.randint(0, 16)
                pyxel.line(line_x, line_y, line_x - 8, line_y, 10)
class HumanEnemy2(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(5, x, y, level)
        self.miss_chance = 0.3
        self.special_ability = "Grenade"
        self.special_cooldown_max = 360  # 6 seconds
        self.special_duration = 10  # Short duration
        self.hp = 35
        self.sprite_left = (0, 64)
        self.sprite_right = (16, 64)
        self.sprite_damage_left = (32, 64)
        self.sprite_damage_right = (48, 64)
        self.sprite_defeated_left = (64, 64)
        self.sprite_defeated_right = (80, 64)

    def activate_special_ability(self, player):
        """Activate grenade throw"""
        # Throw grenade at player position
        self.throw_grenade(player.x + 8, player.y + 8)

    def draw_special_effect(self, x_offset):
        """Draw grenade throw effect"""
        if self.special_active:
            # Draw throwing animation
            throw_x = self.x - x_offset + 8
            throw_y = self.y + 4
            pyxel.pset(throw_x, throw_y, 8)
class HumanEnemy3(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(6, x, y, level)
        self.miss_chance = 0.1
        self.special_ability = "Camouflage"
        self.special_cooldown_max = 420  # 7 seconds
        self.special_duration = 150  # 2.5 seconds
        self.hp = 50
        self.sprite_left = (0, 80)
        self.sprite_right = (16, 80)
        self.sprite_damage_left = (32, 80)
        self.sprite_damage_right = (48, 80)
        self.sprite_defeated_left = (64, 80)
        self.sprite_defeated_right = (80, 80)
        self.original_miss_chance = self.miss_chance

    def activate_special_ability(self, player):
        """Activate camouflage - become harder to hit"""
        self.miss_chance = 0.8  # Much harder to hit when camouflaged

    def deactivate_special_ability(self, player):
        """Deactivate camouflage"""
        self.miss_chance = self.original_miss_chance

    def draw_special_effect(self, x_offset):
        """Draw camouflage effect"""
        if self.special_active:
            # Draw camouflage overlay (semi-transparent)
            if self.facing_direction == 1:  # Right
                pyxel.blt(self.x - x_offset, self.y, 0, 0, 80, 16, 16, 0)
            else:  # Left
                pyxel.blt(self.x - x_offset, self.y, 0, 16, 80, 16, 16, 0)

class HumanEnemy4(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(7, x, y, level)
        self.miss_chance = 0.1
        self.special_ability = "Hacking (placeholder)"
        self.hp = 20
        self.sprite_left = (0, 80)
        self.sprite_right = (16, 80)
        self.sprite_damage_left = (32, 80)
        self.sprite_damage_right = (48, 80)
        self.sprite_defeated_left = (64, 80)
        self.sprite_defeated_right = (80, 80)

class BossEnemy(BaseEnemy):
    def __init__(self, x, y, level=0):
        super().__init__(8, x, y, level)
        self.hp = 1000
        self.weapon = 'Rifle'
        self.weapon_sprites = [
            (0, 160), (8, 160), (0, 168), (8, 168), (16, 160), (24, 160), (16, 168), (24, 168)
        ]
        self.weapon_range = 100
        self.weapon_ai = 'rifle'
        # Sprite locations
        self.sprite_left = (0, 224)
        self.sprite_right = (16, 224)
        self.sprite_damage_left = (96, 224)
        self.sprite_damage_right = (112, 224)
        self.sprite_defeated_left = (128, 224)
        self.sprite_defeated_right = (144, 224)
        # Walking animation
        self.walk_left = [(32, 224), (48, 224)]
        self.walk_right = [(64, 224), (80, 224)]
        self.walk_anim_timer = 0
        self.walk_anim_index = 0
        # Teleport ability
        self.teleport_cooldown_max = 360
        self.teleport_cooldown = 0
        self.teleporting = False
        self.teleport_timer = 0
        self.teleport_duration = 20
        self.teleport_flash_timer = 0
        self.teleport_flash_duration = 8
        self.last_damage_time = -999
        # EMP ability
        self.emp_cooldown_max = 420
        self.emp_cooldown = 0
        self.emp_active = False
        self.emp_wave_time = 30
        self.emp_wave_timer = 0
        self.emp_radius = 0
        self.emp_max_radius = 96
        self.emp_hit = False
        # Shield Overload ability
        self.shield_cooldown_max = 480  # 8 seconds
        self.shield_cooldown = 0
        self.shield_active = False
        self.shield_duration = 90  # 1.5 seconds
        self.shield_timer = 0
        # Summon Minions ability
        self.summon_cooldown_max = 600  # 10 seconds
        self.summon_cooldown = 0
        self.summon_active = False
        self.summon_timer = 0
        self.summon_flash = 0
        self.summon_minions = []
        # Teleport target defaults (for linter)
        self._teleport_new_x = self.x
        self._teleport_new_y = self.y
        # Homing Grenades ability
        self.grenade_cooldown_max = 360  # 6 seconds
        self.grenade_cooldown = 0
        self.grenade_active = False
        self.grenade_timer = 0
        self.homing_grenades = []  # List of {'x','y','vx','vy','timer','alive'}
        # Berserk state
        self.berserk = False
        self.berserk_speed_mult = 1.7
        self.berserk_attack_mult = 0.5  # 2x faster
        # Gravity Well ability
        self.gravitywell_cooldown_max = 540  # 9 seconds
        self.gravitywell_cooldown = 0
        self.gravitywell_active = False
        self.gravitywell_timer = 0
        self.gravitywell_duration = 60  # 1 second
        self.gravitywell_point = (self.x, self.y)
        self.gravitywell_radius = 64
        self.gravitywell_pull_strength = 2.0

    def take_damage(self, amount):
        # If shield is active, ignore damage
        if self.shield_active:
            return
        super().take_damage(amount)
        # Trigger teleport if not on cooldown, not already teleporting, and alive
        if self.alive and self.teleport_cooldown == 0 and not self.teleporting:
            self.start_teleport()

    def start_teleport(self):
        self.teleporting = True
        self.teleport_timer = self.teleport_duration
        self.teleport_flash_timer = self.teleport_flash_duration
        self.teleport_cooldown = self.teleport_cooldown_max
        self.visual_state = "damage"
        self._teleport_old_pos = (self.x, self.y)
        main_floor = self.structure[self.level]["mapFloor"][0]
        fx, fy, fw, fh = main_floor
        min_x = fx + 8
        max_x = fx + fw - 24
        self._teleport_new_x = random.randint(min_x, max_x)
        self._teleport_new_y = fy - 16

    def update(self, player, camera_x=0, enemies=None):
        # Berserk logic
        if not self.berserk and self.hp < 500:
            self.berserk = True
            self.speed *= self.berserk_speed_mult
            self.attack_cooldown_max = int(self.attack_cooldown_max * self.berserk_attack_mult)
        # Gravity Well logic
        if self.gravitywell_active:
            self.gravitywell_timer -= 1
            # Pull player toward gravity well point if in range
            px, py = player.x + 8, player.y + 8
            gx, gy = self.gravitywell_point
            dx = gx - px
            dy = gy - py
            dist = math.hypot(dx, dy)
            if dist < self.gravitywell_radius:
                # Apply pull (reduce if very close)
                pull = self.gravitywell_pull_strength * (1 - dist / self.gravitywell_radius)
                if dist > 2:
                    player.x += int(dx / dist * pull)
                    player.y += int(dy / dist * pull)
            if self.gravitywell_timer <= 0:
                self.gravitywell_active = False
                self.gravitywell_cooldown = self.gravitywell_cooldown_max
            self.is_moving = False
            self.attack_cooldown = self.attack_cooldown_max
        # Homing Grenades logic
        if self.grenade_active:
            self.grenade_timer -= 1
            if self.grenade_timer == 10:
                # Launch 2-3 grenades
                for i in range(random.randint(2, 3)):
                    angle = random.uniform(-0.5, 0.5) + math.atan2(player.y - self.y, player.x - self.x)
                    speed = 2.0
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    grenade = {'x': self.x + 8, 'y': self.y + 8, 'vx': vx, 'vy': vy, 'timer': 90, 'alive': True}
                    self.homing_grenades.append(grenade)
            if self.grenade_timer <= 0:
                self.grenade_active = False
                self.grenade_cooldown = self.grenade_cooldown_max
            self.is_moving = False
            self.attack_cooldown = self.attack_cooldown_max
        # Update homing grenades
        for grenade in self.homing_grenades:
            if not grenade['alive']:
                continue
            # Home in on player
            dx = (player.x + 8) - grenade['x']
            dy = (player.y + 8) - grenade['y']
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                grenade['vx'] += dx * 0.1
                grenade['vy'] += dy * 0.1
                # Clamp speed
                speed = math.hypot(grenade['vx'], grenade['vy'])
                max_speed = 2.5
                if speed > max_speed:
                    grenade['vx'] *= max_speed / speed
                    grenade['vy'] *= max_speed / speed
            grenade['x'] += grenade['vx']
            grenade['y'] += grenade['vy']
            grenade['timer'] -= 1
            # Explosion on timer or close to player
            if grenade['timer'] <= 0 or math.hypot(grenade['x'] - (player.x + 8), grenade['y'] - (player.y + 8)) < 12:
                grenade['alive'] = False
                # Damage player if close
                if math.hypot(grenade['x'] - (player.x + 8), grenade['y'] - (player.y + 8)) < 20:
                    player.take_damage(12)
        # Remove dead grenades
        self.homing_grenades = [g for g in self.homing_grenades if g['alive']]
        # Summon Minions logic
        if self.summon_active:
            self.summon_timer -= 1
            self.summon_flash += 1
            if self.summon_timer == 10 and enemies is not None:
                # Actually spawn minions (2-3 minions)
                for i in range(random.randint(2, 3)):
                    mx = self.x + random.randint(-24, 24)
                    my = self.y
                    minion_type = random.choice([0, 3])  # Robot or Human
                    minion = create_enemy(minion_type, mx, my, self.level)
                    enemies.append(minion)
                    self.summon_minions.append((mx, my))
            if self.summon_timer <= 0:
                self.summon_active = False
                self.summon_cooldown = self.summon_cooldown_max
                self.summon_minions = []
            self.is_moving = False
            self.attack_cooldown = self.attack_cooldown_max
        # Shield Overload logic
        elif self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
                self.shield_cooldown = self.shield_cooldown_max
            self.is_moving = False
            self.attack_cooldown = self.attack_cooldown_max
        # EMP logic
        elif self.emp_active:
            self.emp_wave_timer -= 1
            self.emp_radius = int(self.emp_max_radius * (1 - self.emp_wave_timer / self.emp_wave_time))
            if self.emp_wave_timer == self.emp_wave_time // 2 and not self.emp_hit:
                dx = (self.x + 8) - (player.x + 8)
                dy = (self.y + 8) - (player.y + 8)
                if math.hypot(dx, dy) <= self.emp_max_radius:
                    if hasattr(player, 'apply_emp_debuff'):
                        player.apply_emp_debuff(120)
                    self.emp_hit = True
            if self.emp_wave_timer <= 0:
                self.emp_active = False
                self.emp_cooldown = self.emp_cooldown_max
                self.emp_radius = 0
                self.emp_hit = False
            self.is_moving = False
            self.attack_cooldown = self.attack_cooldown_max
        # Teleport logic (takes priority over all other actions)
        elif self.teleporting:
            self.teleport_timer -= 1
            if self.teleport_flash_timer > 0:
                self.teleport_flash_timer -= 1
            if self.teleport_timer == self.teleport_duration // 2:
                self.x = self._teleport_new_x
                self.y = self._teleport_new_y
            if self.teleport_timer <= 0:
                self.teleporting = False
                self.visual_state = "normal"
        else:
            if self.teleport_cooldown > 0:
                self.teleport_cooldown -= 1
            if self.emp_cooldown > 0:
                self.emp_cooldown -= 1
            if self.shield_cooldown > 0:
                self.shield_cooldown -= 1
            if self.summon_cooldown > 0:
                self.summon_cooldown -= 1
            if self.grenade_cooldown > 0:
                self.grenade_cooldown -= 1
            if self.gravitywell_cooldown > 0:
                self.gravitywell_cooldown -= 1
            # AI: Homing Grenades
            if not self.grenade_active and not self.teleporting and self.grenade_cooldown == 0:
                if random.random() < 0.01:
                    self.grenade_active = True
                    self.grenade_timer = 30
            # AI: Summon Minions
            elif not self.summon_active and not self.teleporting and self.summon_cooldown == 0:
                if random.random() < 0.01:
                    self.summon_active = True
                    self.summon_timer = 30
                    self.summon_flash = 0
                    self.summon_minions = []
            # AI: Shield Overload
            elif not self.shield_active and not self.teleporting and self.shield_cooldown == 0:
                if random.random() < 0.01:
                    self.shield_active = True
                    self.shield_timer = self.shield_duration
            # AI: EMP wave
            elif not self.emp_active and not self.teleporting and self.emp_cooldown == 0:
                if random.random() < 0.01:
                    self.emp_active = True
                    self.emp_wave_timer = self.emp_wave_time
                    self.emp_radius = 0
                    self.emp_hit = False
            # AI: Gravity Well
            elif not self.gravitywell_active and not self.teleporting and self.gravitywell_cooldown == 0:
                if random.random() < 0.01:
                    self.gravitywell_active = True
                    self.gravitywell_timer = self.gravitywell_duration
                    # Target a point near the player (but not directly on top)
                    px, py = player.x + 8, player.y + 8
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.randint(24, 48)
                    gx = px + int(math.cos(angle) * radius)
                    gy = py + int(math.sin(angle) * radius)
                    self.gravitywell_point = (gx, gy)
            super().update(player, camera_x)
        # Walking animation logic
        if self.visual_state == "normal" and self.is_moving:
            self.walk_anim_timer += 1
            if self.walk_anim_timer >= 8:
                self.walk_anim_timer = 0
                self.walk_anim_index = (self.walk_anim_index + 1) % 2

    def draw(self, x_offset=0, target=None):
        # Berserk visual effect
        if self.berserk:
            px = self.x - x_offset
            py = self.y
            pyxel.circb(px + 8, py + 8, 18, 8)
        # Homing Grenades visual
        for grenade in self.homing_grenades:
            if grenade['alive']:
                pyxel.blt(grenade['x'] - x_offset - 4, grenade['y'] - 4, 0, 0, 208, 8, 8, 14)
                pyxel.circb(grenade['x'] - x_offset + 0, grenade['y'] + 0, 10, 10)
        # Summon Minions visual effect
        if self.summon_active:
            for mx, my in self.summon_minions:
                color = 10 if (self.summon_flash // 4) % 2 == 0 else 7
                pyxel.circb(mx - x_offset + 8, my + 8, 12, color)
        # Shield Overload effect
        if self.shield_active:
            px = self.x - x_offset
            py = self.y
            pyxel.circb(px + 8, py + 8, 14, 12)
            pyxel.circb(px + 8, py + 8, 16, 7)
        # EMP wave effect
        if self.emp_active:
            pyxel.circ(self.x - x_offset + 8, self.y + 8, self.emp_radius, 9)
            pyxel.circb(self.x - x_offset + 8, self.y + 8, self.emp_radius, 7)
        # Gravity Well visual effect
        if self.gravitywell_active:
            gx, gy = self.gravitywell_point
            color = 13 if (self.gravitywell_timer // 4) % 2 == 0 else 7
            pyxel.circ(gx - x_offset, gy, self.gravitywell_radius, color)
            pyxel.circ(gx - x_offset, gy, int(self.gravitywell_radius * (self.gravitywell_timer / self.gravitywell_duration)), 10)
            pyxel.text(gx - x_offset - 12, gy - 8, "GRAVITY WELL", 13)
        # Boss health bar
        if isinstance(self, BossEnemy):
            bar_w = 40
            bar_h = 5
            bar_x = self.x - x_offset + 8 - bar_w // 2
            bar_y = self.y - 18
            pct = max(0, self.hp / 1000)
            pyxel.rect(bar_x, bar_y, bar_w, bar_h, 1)
            pyxel.rect(bar_x, bar_y, int(bar_w * pct), bar_h, 8)
            percent_text = f"BOSS {int(pct*100)}%"
            pyxel.text(bar_x, bar_y - 7, percent_text, 8)
        # Teleport flash effect
        if self.teleporting and self.teleport_flash_timer > 0:
            ox, oy = getattr(self, '_teleport_old_pos', (self.x, self.y))
            nx = getattr(self, '_teleport_new_x', self.x)
            ny = getattr(self, '_teleport_new_y', self.y)
            pyxel.circ(ox - x_offset + 8, oy + 8, 12, 10)
            pyxel.circ(nx - x_offset + 8, ny + 8, 12, 10)
        # Draw boss as usual
        if self.visual_state == "defeated":
            sx, sy = self.sprite_defeated_right if self.facing_direction == 1 else self.sprite_defeated_left
        elif self.visual_state == "damage":
            sx, sy = self.sprite_damage_right if self.facing_direction == 1 else self.sprite_damage_left
        elif self.visual_state == "normal" and self.is_moving:
            if self.facing_direction == 1:
                sx, sy = self.walk_right[self.walk_anim_index]
            else:
                sx, sy = self.walk_left[self.walk_anim_index]
        else:
            sx, sy = self.sprite_right if self.facing_direction == 1 else self.sprite_left
        pyxel.blt(self.x - x_offset, self.y, 0, sx, sy, 16, 16, 14)
        if self.visual_state != "defeated":
            self.draw_weapon(x_offset, target)
        # Draw bullets
        for bullet in self.bullets:
            if bullet['alive']:
                pyxel.circ(bullet['x'] - x_offset, bullet['y'], 1, bullet['color'])

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

    def wide_laser_intersects_player(self, x0, y0, x1, y1, player):
        # Check if player rectangle intersects a wide laser beam (width 12)
        px, py, pw, ph = player.x, player.y, 16, 16
        # Sample points along the laser and check if within width
        for t in range(0, 101, 5):
            lx = x0 + (x1 - x0) * t / 100
            ly = y0 + (y1 - y0) * t / 100
            # Distance from player center to laser line
            cx, cy = px + pw/2, py + ph/2
            dist = abs((y1 - y0) * cx - (x1 - x0) * cy + x1*y0 - y1*x0) / (math.hypot(x1 - x0, y1 - y0) + 1e-6)
            if dist < 8 and px <= lx <= px+pw and py <= ly <= py+ph:
                return True
        return False

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
    elif type_index == 8:
        return BossEnemy(x, y, level)
    else:
        return BaseEnemy(type_index, x, y, level) 