import pyxel, PyxelUniversalFont as pul
from src import settings, game_status, player, map, camera
from src.enemy import create_enemy

class Neurotrace:
    
    # === INIT AREA ===

    def __init__(self):
        self.debug_mode = True  # Debug mode flag
        self.god_mode = False   # god mode 
        self.infinite_ammo = False  # infinite ammo 
        self.door_open = False  # Door state
        self.door_proximity_distance = 32  # Distance to trigger door opening
        self.initHelpers()  # Init Game Helpers 
        pyxel.init(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, title=settings.GAME_TITLE, fps=settings.FPS)  # Init the game window
        pyxel.mouse(settings.CURSOR)  # Enable mouse cursor if specified in settings
        # ! Load Resources first before map and player
        # Load resources from file 
        self.initResources()
        # Init Player Module 
        self.initPlayer()
        # Init Map and Camera Module 
        self.initMap()
        # Init Player Postion in the map 
        self.loadMap()
        

    def initHelpers(self):
        """
        Initialize the game helpers for better managing the games 
        """
        self.GAME_STATUS = game_status.GameStatus()

    def initResources(self):
        pyxel.load("src/assets.pyxres")

    def initPlayer(self):
        self.player = player.Player()
        

    def initMap(self):
        self.level = 0
        self.map = map.Map()
        self.camera = camera.Camera()
        # Spawn enemies
        self.enemies = []
        ## Get enemies as defined in the structure 
        for enemy_info in self.map.structure[self.level]["enemies"]:
            type_index, x, y = enemy_info
            self.enemies.append(create_enemy(type_index, x, y, self.level))

    def loadMap(self, level = 0):
        self.player.resetPlayerPos()

    # === END OF INIT AREA === 

    # === RUN SECTION === 
    def run(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        # Toggle debug mode with F3 Key
        if pyxel.btnp(pyxel.KEY_F3):
            self.debug_mode = not self.debug_mode

        if self.debug_mode:
            self.player.speed = 10

        # Toggle god_mode with F4 Key 
        if pyxel.btnp(pyxel.KEY_F4):
            self.god_mode = not self.god_mode

        if pyxel.btnp(pyxel.KEY_F5):
            self.infinite_ammo = not self.infinite_ammo

        # if player in god mode, always in full hp 
        if self.god_mode:
            self.player.health = 400

        # if player in infinite ammo, always in full ammo 
        if self.infinite_ammo:
            self.player.ammo = self.ammo = [8, 30, 10]

        # Reset player movement flag at the start of update
        self.player.is_moving = False 

        # Prevent all actions if player is dead
        if not self.player.alive:
            return
        
        # Player Movement 
        ## Move Left 
        if pyxel.btn(pyxel.KEY_A):
            self.player.moveLeft()

        ## Move Right 
        elif pyxel.btn(pyxel.KEY_D):
            self.player.moveRight()

        ## Jump control
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.player.jump()

        ## Dash control
        if pyxel.btnp(pyxel.KEY_CTRL):
            self.player.dash()

        # Update camera to follow player
        ## Get the map width from the structure 
        map_width = self.map.structure[self.level]["mapWH"][0]
        ## update the camera: to center the player, since player is 16*16, we need to move right and move down 8 (half of the player)
        self.camera.update(self.player.x + 8, self.player.y + 8, map_width)
        ## get camera offset 
        self.camera_x, self.camera_y = self.camera.get_offset()

        # Fire control
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.player.fire(self.camera_x)

        # Portal interaction
        if pyxel.btnp(pyxel.KEY_Z):
            self.check_portal_interaction()
            

        # Check door proximity: if player approaches the portal, the door open. 
        self.check_door_proximity()

        # PLAYER MAIN UPDATE function
        self.player.update(self.level, self.camera_x, self.enemies)

        # ENEMIES MAIN UPDATE function 
        for enemy in self.enemies:
            ## if BOSS summon 
            if hasattr(enemy, 'summon_active'):
                enemy.update(self.player, self.camera_x, self.enemies)
            else:
                ## regular update each enemy 
                enemy.update(self.player, self.camera_x)

        # Check for collisions for player's firing 
        if self.player.is_firing and self.player.fire_line:
            ## get the bullet position 
            x0, y0, x1, y1 = self.player.fire_line
            for enemy in self.enemies:
                ## only check when enemies are still alive 
                if enemy.alive:
                    ## get enemy position 
                    ex, ey = enemy.x, enemy.y 
                    ## if collide, enemy take damage 
                    if self.line_intersects_rect(x0, y0, x1, y1, ex, ey, 16, 16):
                        enemy.take_damage(1)

    def check_portal_interaction(self):
        """
        Check if player is near portal and handle level transition
        function is triggered when player press 'z' to go to next level 
        """
        if "portal" in self.map.structure[self.level]:
            portal = self.map.structure[self.level]["portal"]
            if portal is not None:
                ## get portal position and size
                portal_x, portal_y, portal_w, portal_h = portal
                ## get player positon 
                player_x, player_y = self.player.x, self.player.y
                ## Check if player is within portal area
                if (portal_x <= player_x <= portal_x + portal_w and 
                    portal_y <= player_y <= portal_y + portal_h):
                    ## trigger transition: move the player and let camera follow 
                    self.transition_to_next_level()

    def check_door_proximity(self):
        """Check if player is near the door and update door state"""
        if "portal" in self.map.structure[self.level]:
            portal = self.map.structure[self.level]["portal"]
            if portal is not None:
                ## get portal position [absolute] and size 
                portal_x, portal_y, portal_w, portal_h = portal
                ## get center position of player 
                player_x, player_y = self.player.x + 8, self.player.y + 8  # Player center
                ## Calculate distance between player and door (center)
                door_center_x = portal_x + portal_w // 2
                door_center_y = portal_y + portal_h // 2
                ## calculate the distance using Euclidean distance formula: sqrt((x2 - x1)^2 + (y2 - y1)^2)
                distance = ((player_x - door_center_x) ** 2 + (player_y - door_center_y) ** 2) ** 0.5
                ## Update door state based on proximity
                self.door_open = distance <= self.door_proximity_distance
            else:
                ## door will never open since there is no door 
                self.door_open = False

    def transition_to_next_level(self):
        """Transition to the next level"""
        # increment to game level 
        self.level += 1
        self.player.level += 1
        # print("Function called")
        # self.player.level += 1
        # if the level is in the map 
        if self.level in self.map.structure:
            ## Clear current enemies
            self.enemies = []
            ## Spawn new enemies for the new level
            for enemy_info in self.map.structure[self.level]["enemies"]:
                type_index, x, y = enemy_info
                self.enemies.append(create_enemy(type_index, x, y, self.level))
            ## Reset player position for new level
            self.player.resetPlayerPos(self.level)
        else:
            ## TODO: If no more levels, go back to level 0
            self.level = 0
            self.enemies = []
            for enemy_info in self.map.structure[self.level]["enemies"]:
                type_index, x, y = enemy_info
                self.enemies.append(create_enemy(type_index, x, y, self.level))
            self.player.resetPlayerPos(self.level)

    def draw(self):
        # MAIN DRAWING FUNCTION 
        # clear screen 
        pyxel.cls(0)

        # check if in menu 
        if self.GAME_STATUS.is_menu():
            ## show the game title 
            self.GAME_STATUS.showGameTitle()
        # if in the game 
        elif self.GAME_STATUS.is_playing():
            ## draw the game map (something needs to draw apart from the map itself (most interactable item) such as portal)
            self.map.drawMap(self.level, self.camera_x, self.door_open)

            ## PLAYER MAIN DRAWING function 
            self.player.draw(self.camera_x, self.level)
            ## ENEMIES MAIN DRAWING function 
            for enemy in self.enemies:
                enemy.draw(self.camera_x, target=self.player)
            # Debug 
            if self.debug_mode:
                px, py = int(self.player.x), int(self.player.y)
                pyxel.text(5, 25, f"Player: ({px}, {py})", 11)
                pyxel.text(5, 35, f"God Mode: {"Yes" if self.god_mode else "No"}", 11)
                pyxel.text(5, 45, f"Infinite Ammo: {"Yes" if self.infinite_ammo else "No"}", 11)
            
    def line_intersects_rect(self, x0, y0, x1, y1, rx, ry, rw, rh):
        """This function checks collision"""
        # Simple AABB vs line segment check
        # Check if either endpoint is inside the rect
        if rx <= x0 <= rx+rw and ry <= y0 <= ry+rh:
            return True
        if rx <= x1 <= rx+rw and ry <= y1 <= ry+rh:
            return True
        # Check for intersection with each edge
        ## [CODE referemce from Online]
        ## "line segment intersection" algorithm using the "counter-clockwise (CCW) test" from computational geometry from internet
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

if __name__ == "__main__":
    game = Neurotrace()
    game.run()