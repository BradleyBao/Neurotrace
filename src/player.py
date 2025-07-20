import pyxel, src.structure, src.settings, src.game_status
import math

class Player:
    def __init__(self):
        # import structure 
        self.structure = src.structure.STRUCTURE

        # player position 
        self.x = 0
        self.y = 0

        # map level 
        self.level = 0

        # player speed 
        self.speed = src.settings.PLAYER_SPEED

        # jump and gravity acceleration and velocity 
        self.jump_speed = src.settings.PLAYER_JUMP_SPEED
        self.gravity = src.settings.GRAVITY
        self.velocity_y = 0
        self.is_jumping = False

        # player walking animation 
        self.animation_frame = 0
        self.animation_timer = 0 

        # player facing direction, determine by mouse 
        self.facing_direction = 1  # 1 for right, -1 for left 

        # is moving for animation 
        self.is_moving = False

        # player sprites 
        self.playerLeft = (16, 0)
        self.playerRight = (32, 0)

        # Dash system
        self.is_dashing = False 

        ## Dash distance 
        self.dash_distance = 32  # pixels
        self.dash_speed = 6
        self.dash_cooldown = 0
        self.dash_cooldown_max = 20  # frames
        self.dash_remaining = 0
        self.dash_direction = 1  # 1 for right, -1 for left
        
        # Weapon system
        self.weapons = [
            {'name': 'Pistol', 'color': 0, 'penetrate': False, 'max_ammo': 8},
            {'name': 'Rifle', 'color': 12, 'penetrate': True, 'burst_count': 3, 'burst_delay': 3, 'max_ammo': 30},
            {'name': 'Sniper', 'color': 8, 'penetrate': True, 'max_ammo': 10},
        ]

        ## Weapon index 
        self.current_weapon = 0
        self.bullets = []  # List of bullets: {'x', 'y', 'vx', 'vy', 'color', 'penetrate', 'alive'}
        self.weapon_offset = 5  # 1/3 of 16px
        
        ## Ammo system
        self.ammo = [8, 30, 10]  # Current ammo for each weapon
        
        ## Reload system
        self.reload_cooldown = 0
        self.reload_cooldown_max = 120  # 2 seconds at 60fps
        self.is_reloading = False
        
        ## Burst fire system
        self.burst_firing = False
        self.burst_timer = 0
        self.burst_count = 0
        self.burst_delay = 0
        # 8 directions: 
        # [L, R, R45U, L45U, L45D, R45D, D, U]
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

        ## global weapon sprite size
        self.weapon_w = 8
        self.weapon_h = 8

        # Firing 
        self.is_firing = False
        self.fire_timer = 0
        self.fire_duration = 6  # frames (about 100ms at 60fps)
        self.fire_angle = 0
        self.fire_line = None  # (x0, y0, x1, y1)
        # Load animation frames
        self.loadAnimation()

        # Character Health
        self.health = 400
        self.max_health = 400

        # Determine whether the character is still alive 
        self.alive = True

        # Detemrine whether the character is using the shield
        self.is_shielding = False
        self.normal_speed = self.speed
        self.shield_speed = 0.2  # Slower speed when using shield
        self.shield_stamina = 600  # shield remaining energy 
        self.shield_stamina_max = 600
        self.shield_cooldown = 0  # shield cooldown (frames)
        self.shield_cooldown_max = 600  # 10 seconds

        # EMF debuf from boss ememy 
        self.emp_debuff_timer = 0
        # Flashbang blind effect
        self.flashbang_blind_timer = 0

        # Med kit system
        self.medkits = 10
        self.medkit_heal = 50
        self.medkit_feedback_timer = 0

        # Damage sprite state
        self.visual_state = "normal"  # normal, damage
        self.visual_state_timer = 0
        self.sprite_damage_left = (176, 0)
        self.sprite_damage_right = (192, 0)

    def loadAnimation(self):
        """load animation using sprite location"""
        self.walk_left = [(48, 0), (64, 0)]
        self.walk_right = [(80, 0), (96, 0)]
        self.stand_frame_left = self.playerLeft
        self.stand_frame_right = self.playerRight

    def moveLeft(self):
        """move character to the left"""
        # if not dashing 
        if not self.is_dashing:
            # move position of character depend on the speed
            if self.is_shielding:
                ## if char is shielding 
                self.x -= self.shield_speed
            else:
                self.x -= self.speed
        # character is moving 
        self.is_moving = True
        # dash direction would follow moving direction (not mouse)
        self.dash_direction = -1

    def moveRight(self):
        """move character to the right"""
        if not self.is_dashing:
            # move position of character depend on the speed
            if self.is_shielding:
                ## if char is shielding 
                self.x += self.shield_speed
            else:
                self.x += self.speed
        # character is moving 
        self.is_moving = True
        # dash direction would follow moving direction (not mouse)
        self.dash_direction = 1

    def jump(self):
        """player jump"""
        # you cannot jump while you are in jumping status
        if not self.is_jumping:
            # add velocity to go up
            self.velocity_y = self.jump_speed
            # now the char is jumping 
            self.is_jumping = True

    def dash(self):
        """player dash"""
        # if not in dashing or in cooldown 
        if not self.is_dashing and self.dash_cooldown == 0:
            # now the char is dashing 
            self.is_dashing = True
            # dash_remaining and dash_cooldown is the total distance, which would decrease using frame
            self.dash_remaining = self.dash_distance
            self.dash_cooldown = self.dash_cooldown_max

    # MAIN FIRING LOGIC 
    def fire(self, camera_x=0):
        """Main Player Firing logic"""
        # if get emp, do not allow player fire
        if self.emp_debuff_timer > 0:
            return 
        # if not currently firing 
        if not self.is_firing and not self.burst_firing:
            # Conditions that player cannot fire 
            # Check if player have ammo
            if self.ammo[self.current_weapon] <= 0:
                return  # No ammo, can't fire
            # Check if reloading
            if self.is_reloading:
                return  # Can't fire while reloading
            
            # set the fire lock 
            self.is_firing = True
            # fire duration CD timer added and will be decreamented as frames go
            self.fire_timer = self.fire_duration

            # get player absolute coordinates (need to minus camera due to dead zone), +8 to focus on the center
            # TODO: Maybe I should add offsets for shooting? if I have time
            player_screen_x = self.x - camera_x + 8
            player_screen_y = self.y + 8
            ## get mouse coordinates 
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            # get angle between player and mouse 
            ## tangent to get diagonal line
            angle = math.atan2(my - player_screen_y, mx - player_screen_x)
            # get user current weapon 
            weapon = self.weapons[self.current_weapon]
            # Update weapon sprites for visual model: NEED TO FIX: switch should be before firing not after
            ## define weapon sprites 
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
            
            # Handle different weapon types
            if weapon['name'] == 'Sniper':
                ## If snipers, shooting the laser
                self.fire_angle = angle
                self.fire_line = self.calculate_fire_line(angle, camera_x)
            elif weapon['name'] == 'Rifle': 
                # Start burst fire
                self.burst_firing = True
                ## Set Burst Fire Count 
                self.burst_count = weapon['burst_count'] 
                self.burst_delay = weapon['burst_delay'] 
                self.fire_bullet(angle, weapon, camera_x)
            else:
                # Pistol - single shot
                self.fire_bullet(angle, weapon, camera_x)

    def fire_bullet(self, angle, weapon, camera_x=0):
        """Helper method to create and fire a bullet"""
        # Consume ammo
        self.ammo[self.current_weapon] -= 1
        
        # Rifle has a higher shooting speed then other two 
        speed = 8 if weapon['name'] == 'Rifle' else 5

        # Lower the speed of sniper (TBD)
        # speed = 3 if weapon['name'] == "Sniper" else 5

        # Use the sin and cos to get x and y and calculate the speed of x and y
        ## the structure contains: position, velocity of x and y, color of bullets (rifal: blue; pistal: black), rifal is penetratable 
        bullet = {'x': self.x + 8 + math.cos(angle) * 2,
                  'y': self.y + 8 + math.sin(angle) * 2,
                  'vx': math.cos(angle) * speed,
                  'vy': math.sin(angle) * speed,
                  'color': weapon['color'],
                  'penetrate': weapon['penetrate'],
                  'alive': True,
                  'damage': 1 if weapon['name']=='Pistol' else 2}
        ## rifal can penetrate two enemies 
        if weapon['name'] == 'Rifle':
            bullet['penetrate_count'] = 2

        ## store the bullets into all bullets 
        self.bullets.append(bullet)

    def reload_weapon(self):
        """reload the current weapon"""
        if not self.is_reloading and self.reload_cooldown == 0:
            # reload lock 
            self.is_reloading = True
            self.reload_cooldown = self.reload_cooldown_max

    def apply_emp_debuff(self, duration):
        """apply emp debuff: temp disable weapon"""
        self.emp_debuff_timer = duration

    # === MAIN PLAYER FUNCTION ===
    # MAIN PLAYER UPDATE
    def update(self, level=0, camera_x=0, enemies=None):
        # If dead, disable all actions and set game status to Game Over
        if not self.alive:
            self.is_moving = False
            
            return

        # Mouse-based facing
        ## get player center absolute position
        player_cx = self.x + 8
        player_cy = self.y + 8
        ## get mouse coordinate
        mouse_x = pyxel.mouse_x + camera_x
        mouse_y = pyxel.mouse_y

        ## get distance between mouse x and player position
        dx = mouse_x - player_cx
        ## Facing is right if mouse is to the right, else left
        self.facing_direction = 1 if dx >= 0 else -1

        # Dash logic
        if self.is_dashing:
            # print(self.dash_remaining)
            ## calculate the step that dash, if smaller than dash remaining distance, dash the rest 
            dash_step = min(self.dash_speed, self.dash_remaining)
            self.x += dash_step * self.dash_direction
            ## decrement to the remaining dash distance
            self.dash_remaining -= dash_step
            ## stop dashing if remaining distance is zero, negative added for safety check
            if self.dash_remaining <= 0:
                self.is_dashing = False
        ## in dash cd
        elif self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        # in emp debuff cd 
        if self.emp_debuff_timer > 0:
            self.emp_debuff_timer -= 1
        # Flashbang blind effect timer
        if self.flashbang_blind_timer > 0:
            self.flashbang_blind_timer -= 1
        # WEAPON swtich function 
        ## weapon cannot be switched if emped
        if self.emp_debuff_timer == 0:
            ## Q switch to left
            if pyxel.btnp(pyxel.KEY_Q):
                self.current_weapon = (self.current_weapon - 1) % len(self.weapons)
            ## E switch to right 
            if pyxel.btnp(pyxel.KEY_E):
                self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
        # Reload weapon (cannot reload in emp effect)
        if self.emp_debuff_timer == 0 and pyxel.btnp(pyxel.KEY_R):
            self.reload_weapon()
        
        # in reload cd
        if self.is_reloading:
            self.reload_cooldown -= 1
            ## if reload finished, safe check 
            if self.reload_cooldown <= 0:
                ## Finish reload
                weapon = self.weapons[self.current_weapon]
                ## reassign the ammo with max
                self.ammo[self.current_weapon] = weapon['max_ammo']
                ## unlock reloading lock
                self.is_reloading = False
        # in firing 
        if self.is_firing:
            ## fire cd 
            self.fire_timer -= 1
            ## finished firing 
            if self.fire_timer <= 0:
                ## unlock fire lock
                self.is_firing = False
                self.fire_line = None
        
        # in burst fire, when firing, fire function called  
        if self.burst_firing:
            self.burst_delay -= 1
            ## finished burst fire 
            if self.burst_delay <= 0:
                weapon = self.weapons[self.current_weapon]
                ## weapon check: has to be rifle and stil in burst firing 
                if weapon['name'] == 'Rifle' and self.burst_count > 1:
                    ## Fire next bullet in burst
                    ### recalculate init position of bullets 
                    player_screen_x = self.x - camera_x + 8
                    player_screen_y = self.y + 8
                    mx = pyxel.mouse_x
                    my = pyxel.mouse_y
                    ### calculate angle and fire
                    angle = math.atan2(my - player_screen_y, mx - player_screen_x)
                    self.fire_bullet(angle, weapon, camera_x)
                    ## remaining bullets decrement 
                    self.burst_count -= 1
                    self.burst_delay = weapon['burst_delay']
                else:
                    # End burst
                    ## unlock burst fire lock
                    self.burst_firing = False
                    self.burst_count = 0
        # UPDATE bullets
        for bullet in self.bullets:
            ## check if bullets are alive, if not do not render
            if not bullet['alive']:
                continue
            ## update linear position
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            # Remove if out of bounds: x is 2560 and y is 128 (has to be full map because rendering in absolute) 
            if bullet['x'] < 0 or bullet['x'] > 2560 or bullet['y'] < 0 or bullet['y'] > 128:
                ## if out of bounds, remove it
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
                    ## ignore dead enemies 
                    if not enemy.alive:
                        continue
                    ## collsion check, enemies are 16*16
                    if (enemy.x < bullet['x'] < enemy.x+16 and enemy.y < bullet['y'] < enemy.y+16):
                        ## target enemy take damage
                        enemy.take_damage(bullet.get('damage', 1))
                        ## peneration check, if enable, decrement
                        if bullet.get('penetrate_count') is not None:
                            bullet['penetrate_count'] -= 1
                            ## if no more penetration, elimnate 
                            if bullet['penetrate_count'] <= 0:
                                bullet['alive'] = False
                        ## bullets with no penetration 
                        elif not bullet['penetrate']:
                            bullet['alive'] = False

        # refresh bullets, leaving only live bullets 
        self.bullets = [b for b in self.bullets if b['alive']]

        # Sniper line damage - special weapon 
        ## fire only if weapon is sniper and enemy and firing, only calcualte for several frames 
        if self.weapons[self.current_weapon]['name'] == 'Sniper' and self.is_firing and self.fire_line and enemies: 
            ## get current live fire line position 
            x0, y0, x1, y1 = self.fire_line

            ## check collision with enemies 
            for enemy in enemies:
                if not enemy.alive:
                    continue
                ex, ey = enemy.x, enemy.y
                if self.line_intersects_rect(x0, y0, x1, y1, ex, ey, 16, 16):
                    enemy.take_damage(5)

        # Apply gravity
        ## simple simulated calculation, every time is two times the acceleration 
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Clamp player x position to map walls
        map_walls = self.structure[level]["mapWall"]

        ## map walls should have two, safe check
        if len(map_walls) >= 2:
            left_wall = map_walls[0]
            right_wall = map_walls[1]
            min_x = left_wall[0] + left_wall[2]  # right edge of left wall
            max_x = right_wall[0] - 16           # left edge of right wall minus player width

            ## if player positon is surpassing the wall, make them equal (stop them from moving towards the wall)
            if self.x < min_x:
                self.x = min_x
            if self.x > max_x:
                self.x = max_x

        # even though the floor collision is checking, for safety, mandeteory adding height limit to prevent player from falling 
        map_height = self.structure[level]["mapWH"][1]
        if self.y > map_height:
            self.y = map_height
            self.velocity_y = 0

        # Check floor collision
        self.checkFloorCollision(level)

        # Update animation
        ## animation while moving
        if self.is_moving:
            ### set animation index 
            self.animation_timer += 1
            ### if index reached the end of array, reset
            if self.animation_timer >= src.settings.ANIMATION_SPEED:  # Animation speed
                self.animation_frame = (self.animation_frame + 1) % 2
                self.animation_timer = 0
        else:
            # Reset animation when not moving
            self.animation_frame = 0
            self.animation_timer = 0

        # Shield Logic 
        ## if not emped 
        if self.emp_debuff_timer == 0:
            ### if player hold shift and stamina is still alive and not in cd 
            if pyxel.btn(pyxel.KEY_SHIFT) and self.shield_stamina > 0 and self.shield_cooldown == 0:
                #### set shield lock 
                self.is_shielding = True
                #### set to shield speed 
                self.speed = self.shield_speed
                #### consume energy 
                self.shield_stamina -= 1

                #### if no energy, reset 
                if self.shield_stamina <= 0:
                    self.shield_stamina = 0
                    ##### unlock shield lock 
                    self.is_shielding = False
                    ##### add shield cd (overheating penalty)
                    self.shield_cooldown = self.shield_cooldown_max
                    ##### switch back the speed 
                    self.speed = self.normal_speed
            ### if not able to engage shield, reset to normal status 
            else:
                if self.is_shielding:
                    self.speed = self.normal_speed
                self.is_shielding = False
                #### in cd, decrement 
                if self.shield_cooldown > 0:
                    self.shield_cooldown -= 1
                elif self.shield_stamina < self.shield_stamina_max:
                    self.shield_stamina += 1
        ### if emped, forced to cancel the shield
        else:
            self.is_shielding = False
            self.speed = self.normal_speed
        
        # Med kit use (press X), not able to use when emped 
        if self.emp_debuff_timer == 0 and pyxel.btnp(pyxel.KEY_X):
            ## having avilable meds and not able to use it in full health 
            if self.medkits > 0 and self.health < self.max_health:
                self.medkits -= 1
                ### preventing surpass max health 
                self.health = min(self.max_health, self.health + self.medkit_heal)
                ### show med info for .5s 
                self.medkit_feedback_timer = 30  # Show feedback for 0.5s
        # Med kit feedback timer for drawing 
        if self.medkit_feedback_timer > 0:
            self.medkit_feedback_timer -= 1

        # Update damage sprite timer
        if self.visual_state == "damage":
            self.visual_state_timer -= 1
            if self.visual_state_timer <= 0 and self.health > 0:
                self.visual_state = "normal"

    def calculate_fire_line(self, angle, camera_x=0):
        """
        helper function for sniping fireline
        :return the coordinate of init x init y end x end y of fire line of snipers 
        """
        # print(self.level)
        # Start at gun muzzle
        ## calculate player center (cricle)
        player_cx = self.x + 8
        player_cy = self.y + 8
        ## calculate muzzle based on player's absolute coordinate
        muzzle_x = int(player_cx + math.cos(angle) * 8)
        muzzle_y = int(player_cy + math.sin(angle) * 8)
        # Step along the line until hit floor or map edge
        max_length = 256  # only for two chunkcs to increase difficulty 

        # check every two pixels (opt: it would be so inefficient to use 1)
        step = 2
        # check all lines pixels for collision for rendering 
        for l in range(0, max_length, step):
            ## get current frame's line's coordinate 
            tx = int(muzzle_x + math.cos(angle) * l)
            ty = int(muzzle_y + math.sin(angle) * l)
            # Check map bounds (world coordinates)
            ## ! the bound is absolute, has to be full bound
            ## if outside the bound
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
        """helper function to check if player collide with the floor"""
        floors = self.structure[level]["mapFloor"]
        # Check if player is on any floor
        ## on floor lock
        on_floor = False

        ## check all floors 
        for i, floor in enumerate(floors):
            floor_x, floor_y, floor_w, floor_h = floor
            # Check if player is above the floor and falling
            if (self.x < floor_x + floor_w and 
                self.x + 16 > floor_x and 
                self.y + 16 >= floor_y and 
                self.y + 16 <= floor_y + floor_h + 5):  # Added tolerance for landing
                # Land on floor, calculate in 16*16 
                self.y = floor_y - 16
                ## set character not to fall 
                self.velocity_y = 0
                ## reset jumping lock, enable jumping 
                self.is_jumping = False
                on_floor = True
                break
        # If not on any floor, player is jumping
        if not on_floor:
            self.is_jumping = True

    def resetPlayerPos(self, level=0):
        """helper function to reset player status and position, will reset every level"""
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
        """helper function to determine which direction is pointing for sprites rendering"""
        # 8 directions: [L, R, R45U, L45U, L45D, R45D, D, U]
        ## get player positon in center
        player_screen_x = self.x - camera_x + 8
        player_screen_y = self.y + 8
        ## get mouse position [relative]
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        ## calculate angle that pointing towards cursor
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
        """helper function to draw weapon"""
        # get center player position 
        player_screen_x = self.x - x_offset + 8
        player_screen_y = self.y + 8
        # get mouse position [relative]
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        # calculate angle towards mouse
        angle = math.atan2(my - player_screen_y, mx - player_screen_x)
        # calculate in degree not radian 
        angle_deg = math.degrees(angle)
        # get weapon direction index 
        idx = self.get_weapon_direction_index_from_angle(angle_deg)
        # in fire, switch to corresponding firing sprites 
        if self.is_firing or self.burst_firing:
            sx, sy = self.weapon_fire_sprites[idx]
        # if not, switch to normal firing sprites 
        else:
            sx, sy = self.weapon_sprites[idx]
        # screen coordinates where the weapon sprite should be drawn using relative player coordinates 
        # (sprite of weapon is 8*8 and rendered in the center of weapon's width)
        wx = int(player_screen_x + math.cos(angle) * 8 - self.weapon_w // 2)
        wy = int(player_screen_y + math.sin(angle) * 8 - self.weapon_h // 2)
        # main weapon rendering function 
        pyxel.blt(wx, wy, 0, sx, sy, self.weapon_w, self.weapon_h, 14)
        # draw the fire line
        if self.is_firing and self.fire_line:
            x0, y0, x1, y1 = self.fire_line
            pyxel.line(x0 - x_offset, y0, x1 - x_offset, y1, 8)

    def get_weapon_direction_index_from_angle(self, angle):
        """
        helper function to get weapon direction sprite
        :return integer that stands for which angle to render 
        """
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

    # MAIN PLAYER DRAWING FUNCTION
    def draw(self, x_offset=0, camera_x=0, level=0):
        # Draw player death sprite if dead
        if not self.alive:
            ## minus offset for deadzone 
            if self.facing_direction == 1:  # Right
                pyxel.blt(self.x - x_offset, self.y, 0, 160, 0, 16, 16, 14)
            else:  # Left
                pyxel.blt(self.x - x_offset, self.y, 0, 144, 0, 16, 16, 14)
            # Draw health bar and text as zero
            ## minus offset for deadzone 
            bar_x = self.x - x_offset
            bar_y = self.y - 8
            bar_w = 16
            bar_h = 2
            pyxel.rect(bar_x, bar_y, 0, bar_h, 8)
            pyxel.text(5, 2, f"HP: 0/{self.max_health}", 7)
            return

        # Draw player sprite
        if self.visual_state == "damage":
            # Draw damage sprite
            if self.facing_direction == 1:
                pyxel.blt(self.x - x_offset, self.y, 0, self.sprite_damage_right[0], self.sprite_damage_right[1], 16, 16, 14)
            else:
                pyxel.blt(self.x - x_offset, self.y, 0, self.sprite_damage_left[0], self.sprite_damage_left[1], 16, 16, 14)
        elif self.is_moving:
            # Draw walking animation via index
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
        ## calculate health ratio 
        health_ratio = self.health / self.max_health
        pyxel.rect(bar_x, bar_y, int(bar_w * health_ratio), bar_h, 8)
        # Draw player health text
        pyxel.text(5, 2, f"HP: {self.health}/{self.max_health}", 7)
        # Draw ammo text
        weapon = self.weapons[self.current_weapon]
        ammo_color = 7 if self.ammo[self.current_weapon] > 0 else 8  # White if has ammo, red if empty
        
        # Draw weapons 
        if self.weapons[self.current_weapon]['name'] == 'Sniper':
            sniper_sprite = (8, 192)
            icon_x = 12
            icon_y = pyxel.height - 12
            pyxel.blt(icon_x, icon_y, 0, sniper_sprite[0], sniper_sprite[1], 8, 8, 14)
        elif self.weapons[self.current_weapon]['name'] == "Rifle":
            rifal_sprite = (0, 200)
            icon_x = 12
            icon_y = pyxel.height - 12
            pyxel.blt(icon_x, icon_y, 0, rifal_sprite[0], rifal_sprite[1], 8, 8, 14)

        else:
            pistal_sprite = (8, 200)
            icon_x = 12
            icon_y = pyxel.height - 12
            pyxel.blt(icon_x, icon_y, 0, pistal_sprite[0], pistal_sprite[1], 8, 8, 14)

        # Draw reload progress if reloading
        if self.is_reloading:
            reload_progress = 1.0 - (self.reload_cooldown / self.reload_cooldown_max)
            bar_width = 8
            bar_height = 2
            bar_x = 12
            bar_y = pyxel.height - 3
            pyxel.rect(bar_x, bar_y, bar_width, bar_height, 8)  # Background
            pyxel.rect(bar_x, bar_y, int(bar_width * reload_progress), bar_height, 10)  # Progress
            # pyxel.text(bar_x, bar_y - 8, "RELOADING", 10)
        else:
            # if not reloading, show the remaining ammo 
            # pyxel.text(12, pyxel.height - 4, f"{self.ammo[self.current_weapon]}/{weapon['max_ammo']}", ammo_color)
            pyxel.text(12, pyxel.height - 4, f"{self.ammo[self.current_weapon]}", ammo_color)
        
        # Draw portal interaction hint if near portal (ONLY FOR FIRST LEVEL, deprecated due to not functioning)
        # check if the level exist first 
        if self.level < len(self.structure) and "portal" in self.structure[self.level]:
            portal_x, portal_y, portal_w, portal_h = self.structure[self.level]["portal"]
            # print(portal_x, portal_y, portal_w, portal_h)
            # Use player center coordinates to match portal interaction logic
            player_center_x = self.x + 8
            player_center_y = self.y + 8
            if (portal_x <= player_center_x <= portal_x + portal_w and 
                portal_y <= player_center_y <= portal_y + portal_h):
                pyxel.text(5, 35, "Press Z to enter portal", 10)
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
        # EMP debuff visual effect
        if self.emp_debuff_timer > 0:
            px = int(self.x - x_offset)
            py = int(self.y)
            pyxel.circb(px + 8, py + 8, 14, 9)
            pyxel.circb(px + 8, py + 8, 16, 7)
        # Draw med kit count and feedback
        pyxel.blt(22, pyxel.height - 12, 0, 8, 208, 8, 8, 14)  # Med kit icon 
        pyxel.text(20, pyxel.height - 4, f"x{self.medkits}", 7)
        if self.medkit_feedback_timer > 0:
            pyxel.text(self.x - x_offset, self.y - 20, f"+{self.medkit_heal} HP", 11)

        # Draw flashbang blinding overlay
        if hasattr(self, 'flashbang_blind_timer') and self.flashbang_blind_timer > 0:
            pyxel.rect(0, 0, pyxel.width, pyxel.height, 7)

    @staticmethod
    def line_intersects_rect(x0, y0, x1, y1, rx, ry, rw, rh):
        """help function that do collision check"""
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
        """helper function that take damage"""
        # shielding would still cause damage (maybe too hard I should just not taking damage)
        if self.is_shielding:
            amount = (amount + 1) // 2  # Halve and round up
        self.health -= amount
        # Switch to damage sprite
        self.visual_state = "damage"
        self.visual_state_timer = 10  # Show damage sprite for 10 frames
        ## player is dead 
        if self.health <= 0:
            self.health = 0
            self.alive = False
            