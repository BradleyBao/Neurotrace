import pyxel, PyxelUniversalFont as pul
from src import settings, game_status, player, map, camera
from src.enemy import create_enemy

class Neurotrace:
    
    # === INIT AREA ===

    def __init__(self):
        self.initHelpers()  # Init Game Helpers 
        pyxel.init(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, title=settings.GAME_TITLE, fps=settings.FPS)  # Init the game window
        pyxel.mouse(settings.CURSOR)  # Enable mouse cursor if specified in settings
        # ! Load Resources first before map and player
        self.initResources()
        self.initPlayer()
        self.initMap()
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
        # Reset player movement flag at the start of update
        self.player.is_moving = False
        
        # Player Movement 
        if pyxel.btn(pyxel.KEY_A):
            # Move Left 
            self.player.moveLeft()

        elif pyxel.btn(pyxel.KEY_D):
            # Move Right 
            self.player.moveRight()

        # Jump control
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.player.jump()

        # Dash control
        if pyxel.btnp(pyxel.KEY_CTRL):
            self.player.dash()

        # Update camera to follow player
        map_width = self.map.structure[self.level]["mapWH"][0]
        self.camera.update(self.player.x + 8, self.player.y + 8, map_width)
        self.camera_x, self.camera_y = self.camera.get_offset()

        # Fire control
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.player.fire(self.camera_x)

        # Update player physics and animations
        self.player.update(self.level, self.camera_x)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player, self.camera_x)

    def draw(self):
        pyxel.cls(0)
        if self.GAME_STATUS.is_menu():
            self.GAME_STATUS.showGameTitle()

        if self.GAME_STATUS.is_playing():
            self.map.drawMap(self.level, self.camera_x)
            self.player.draw(self.camera_x)
            for enemy in self.enemies:
                enemy.draw(self.camera_x)
            
    
if __name__ == "__main__":
    game = Neurotrace()
    game.run()