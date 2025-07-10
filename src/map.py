import pyxel, src.structure

class Map():
    def __init__(self):
        self.structure = src.structure.STRUCTURE

    def drawMap(self, level=0, camera_x=0, door_open=False):
        pyxel.bltm(-camera_x, 0, 0, 
                   self.structure[level]["mapUV"][0], 
                   self.structure[level]["mapUV"][1], 
                   self.structure[level]["mapWH"][0], 
                   self.structure[level]["mapWH"][1], 0)
        
        # Draw portal if it exists in this level
        if "portal" in self.structure[level]:
            portal_x, portal_y, portal_w, portal_h = self.structure[level]["portal"]
            # Draw closed door sprite at (0, 72) - always visible
            
            # Draw open door sprite on top when door is open
            if door_open:
                pyxel.blt(portal_x - camera_x, portal_y, 1, 0, 80, portal_w, portal_h, 0)
            else:
                pyxel.blt(portal_x - camera_x, portal_y, 1, 32, 0, portal_w, portal_h, 0)
        