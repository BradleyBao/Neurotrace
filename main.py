import pyxel, PyxelUniversalFont as pul
from src import settings, game_status, player

class Neurotrace:
    
    # === INIT AREA ===

    def __init__(self):
        self.initHelpers()  # Init Game Helpers 
        pyxel.init(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, title=settings.GAME_TITLE, fps=settings.FPS)  # Init the game window
        pyxel.mouse(settings.CURSOR)  # Enable mouse cursor if specified in settings
        # ! Load Resources first before map and player
        self.initResources()
        self.initPlayer()
        

    def initHelpers(self):
        """
        Initialize the game helpers for better managing the games 
        """
        self.GAME_STATUS = game_status.GameStatus()

    def initResources(self):
        pyxel.load("src/assets.pyxres")

    def initPlayer(self):
        self.player = player.Player()

    # === END OF INIT AREA === 

    # === RUN SECTION === 
    def run(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)
        if self.GAME_STATUS.is_menu():
            self.GAME_STATUS.showGameTitle()

        if self.GAME_STATUS.is_playing():
            self.player.playerStand()
    
if __name__ == "__main__":
    game = Neurotrace()
    game.run()