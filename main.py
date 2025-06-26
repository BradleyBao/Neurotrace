import pyxel, PyxelUniversalFont as pul
from src import settings, game_status

class Neurotrace:
    
    # === INIT AREA ===

    def __init__(self):
        self.initHelpers()  # Init Game Helpers 
        pyxel.init(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, title=settings.GAME_TITLE, fps=settings.FPS)  # Init the game window
        pyxel.mouse(settings.CURSOR)  # Enable mouse cursor if specified in settings
        

    def initHelpers(self):
        """
        Initialize the game helpers for better managing the games 
        """
        self.GAME_STATUS = game_status.GameStatus()

    # === END OF INIT AREA === 

    # === RUN SECTION === 
    def run(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        if self.GAME_STATUS.is_menu():
            self.GAME_STATUS.showGameTitle()
    
if __name__ == "__main__":
    game = Neurotrace()
    game.run()