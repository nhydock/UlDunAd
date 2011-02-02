'''

2010 Nicholas Hydock
UlDunAd
Ultimate Dungeon Adventure

Licensed under the GNU General Public License V3
     http://www.gnu.org/licenses/gpl.html

'''

from sysobj import *
from View import *

from Actor import Family

from MenuObj import MenuObj

class EquipmentButtons(MenuObj):
    def __init__(self, scene):
        self.scene = scene
        self.engine = scene.engine
        
        scenepath = os.path.join("scenes", "menusystem", "equipment")
        self.buttonTex = Texture(os.path.join(scenepath, "icon.png"))
        
        #these buttons are placed up along the right side of the character image
        self.commandsV = ["weapon", "weapon", "accessory", "accessory", "accessory"]
        #these buttons are placed below the character image
        self.commandsH = ["helmet", "armor", "gloves", "legs", "feet"]
        
        self.commandButtonsV = [ImgObj(Texture(os.path.join(scenepath, command + ".png")), 
                                       boundable = True, frameY = 2)
                                for command in self.commandsV]
        self.commandButtonsH = [ImgObj(Texture(os.path.join(scenepath, command + ".png")), 
                                       boundable = True, frameY = 2)
                                for command in self.commandsH]
    
        self.activeArea = 0     #0 = bottom, 1 = side
        self.index = 0          
        
    def buttonClicked(self, image):
        if image in self.commandButtonsH:
            index = self.commandButtonsH.index(image)
            if self.index == index:
                self.scene.select(index)
            self.activeArea = 0
            return True
        if image in self.commandButtonsV:
            self.index = self.commandButtonsH.index(image)
            self.activeArea = 1
            return True
        return False
    
    def keyPressed(self, key, char):
        
class EquipmentScene(Scene):
    def __init__(self, engine):
        self.engine = engine
        
        self.step = 0   #0 = equipment selection, 1 = item selection for replacement
        
        
    def buttonClicked(self, image):
        if self.EquipMenu.buttonClicked(image):
            self.step = 0
        elif self.ItemMenu.buttonClicked(image):
            self.step = 1
                
    def keyPressed(self, key, char):
        if self.step == 0:
            self.EquipMenu.keyPressed(key)
        else:
            self.ItemMenu.keyPressed(key)
        
    def select(self, index):
        if index == 0:
            self.engine.viewport.changeScene("CreateFamily")
        elif index == 1:
            #forcing for testing purposes
            #self.engine.family = Family("default")
            #self.engine.viewport.changeScene("MapList")
            self.engine.viewport.changeScene("FamilyList")
        else:
            self.engine.finished = True
        
    def run(self):
        pass
        
    def render(self, visibility):
        self.background.draw()     
        
        self.menu.render(visibility)
