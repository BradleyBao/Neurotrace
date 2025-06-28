import pyxel, src.structure

class Map():
    def __init__(self):
        self.structure = src.structure.STRUCTURE

    def drawMap(self, level=0, camera_x=0):
        pyxel.bltm(-camera_x, 0, 0, 
                   self.structure[level]["mapUV"][0], 
                   self.structure[level]["mapUV"][1], 
                   self.structure[level]["mapWH"][0], 
                   self.structure[level]["mapWH"][1], 0)
        