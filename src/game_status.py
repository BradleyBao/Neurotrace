"""
game_status_helper.py
This module provides helper functions to manage the game status in the Neurotrace game.
"""
import pyxel, src.settings, PyxelUniversalFont as pul
class GameStatus:
    status = 0
    def __init__(self):
        # self.status = 0 # Init Game Status
        self.previous_status = 0    # Init Previous Game Status 
        self.initFonts()
    def is_menu(self):
        """
        Check if the game is in the menu state.
        :return: bool - True if the game is in the menu state, False otherwise.
        """
        return self.status == 0
    
    def is_playing(self):
        """
        Check if the game is currently being played.
        :return: bool - True if the game is in the playing state, False otherwise.
        """
        return self.status == 1
    
    def is_paused(self):
        """
        Check if the game is paused.
        :return: bool - True if the game is in the paused state, False otherwise.
        """
        return self.status == 2
    
    def is_game_over(self):
        """
        Check if the game is over.
        :return: bool - True if the game is in the game over state, False otherwise.
        """
        return self.status == 3
    
    def is_settings(self):
        """
        Check if the game settings menu is open.
        :return: bool - True if the game is in the settings state, False otherwise.
        """
        return self.status == 4

    def is_winning(self):
        return self.status == 5

    def set_status(self, new_state):
        """
        Set the current game state to a new state.
        :param new_state: str - The new state of the game (e.g., "menu", "playing", "paused", "game_over").
        """
        self.status = new_state

    def get_status(self):
        """
        Get the current game state.
        :return: str - The current state of the game.
        """
        return self.status
    
    def initFonts(self):
        self.title_writer = pul.Writer("misaki_gothic.ttf")
    
    def showGameTitle(self):
        """
        Display the main menu of the game.
        This method will be called when the game is in the menu state.
        """
        # Draw the menu background
        pyxel.cls(0)
        title_content = src.settings.GAME_TITLE
        subtitle_content = "Press SPACE to start"
        title_size = 22
        subtitle_size = 10
        title_x = 15
        title_y = src.settings.WINDOW_HEIGHT // 4
        subtitle_x = 15
        subtitle_y = 85
        # Draw the title text in the center of the window
        self.title_writer.draw(title_x, title_y, title_content, title_size, 7)
        self.title_writer.draw(subtitle_x, subtitle_y, subtitle_content, subtitle_size, 7) 

    def showGameOver(self):
        """
        Display the game over of the game. 
        """
        content = "YOU DIED"
        subtitle_content = "Press R to restart"
        size = 22 
        subtitle_size = 10
        x = 15 
        y = src.settings.WINDOW_HEIGHT // 4
        subtitle_x = 15
        subtitle_y = 85

        self.title_writer.draw(x, y, content, size, 8) 
        self.title_writer.draw(subtitle_x, subtitle_y, subtitle_content, subtitle_size, 8) 

    def showWinning(self):
        """
        Display the game over of the game. 
        """
        content = "YOU WIN"
        subtitle_content = "Press R to restart"
        size = 22 
        subtitle_size = 10
        x = 15 
        y = src.settings.WINDOW_HEIGHT // 4
        subtitle_x = 15
        subtitle_y = 85

        self.title_writer.draw(x, y, content, size, 10) 
        self.title_writer.draw(subtitle_x, subtitle_y, subtitle_content, subtitle_size, 10) 

    