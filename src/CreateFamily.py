'''

2010 Nicholas Hydock
UlDunAd
Ultimate Dungeon Adventure

Licensed under the GNU General Public License V3
     http://www.gnu.org/licenses/gpl.html

'''

from sysobj import *
from View   import *
from Actor  import *

import string

from MenuObj import MenuObj

class CreateFamily(Scene):
    def __init__(self, engine):
        self.engine = engine

        scenepath = os.path.join("scenes", "creation")
        self.background = ImgObj(Texture(os.path.join(scenepath, "creation.png")))
        self.window = WinObj(Texture(os.path.join(scenepath, "window.png")), self.engine.w/4, 0)
        self.button = ImgObj(Texture("ok.png"), boundable = True, frameX = 2)
        self.font   = FontObj("default.ttf")

        self.menu       = MenuObj(self, commands = ["Easy", "Normal", "Hard"], 
                                  position = (400, 330))
        
        #family info
        self.name = []          #name of the family
        self.diffselected = 1   #the difficulty selected (match up number with position in difficulty array
                                # (1 = default, Normal difficulty)

        self.fadeIn     = True  #are the windows transitioning in or out

        self.error = False      #was an error thrown
        self.step = 0           #step 0 = naming, step 1 = choose difficulty
        
        self.exists = False

    def buttonClicked(self, image):
        pass
        
    def keyPressed(self, key, char):
        if self.step == 0:
            #name is a maximum of 13 letters
            if len(self.name) < 13:
                if (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z'):
                    self.name.append(char)
                if len(self.name) > 0:  #can not have the first character be a blank
                    if key == K_SPACE:
                        self.name.append(" ")

            if len(self.name) > 0:
                #can only delete letters if there are some to delete
                if key == K_BACKSPACE:
                    self.name.pop(-1)
                if key == K_RETURN and not self.exists:
                    self.next()
        elif self.step == 1:
                    
            self.menu.keyPressed(key)                

    def select(self, index):
        self.diffselected = index
        self.create()
                    
    def run(self):
        self.exists = os.path.exists(os.path.join("..", "data", "actors", "families", string.join(self.name,'')))
        
    def next(self):
        if self.step == 0 and not self.name:
            self.error = True
        else:
            self.step += 1

    def renderNaming(self):
        w, h = self.engine.w, self.engine.h
        self.window.setPosition(w/2, h/2)
        self.window.setDimensions(w*.4, h*.15)
        self.window.draw()
        
        if self.window.scale[0] == w*.4 and self.window.scale[1] == h*.15:
            self.engine.drawText(self.font, "Enter a name", (w*.5, h*.6))
            name = string.join(self.name, '')
            self.engine.drawText(self.font, name, (w*.5, h*.5))

            if name:
                if self.exists:
                    frame = 2
                else:
                    frame = 1
                self.engine.drawImage(self.button, position = (w*.25, h*.5), scale = (75,75), frameX = frame)
            
                
    def renderDifficulty(self):
        w, h = self.engine.w, self.engine.h
        self.window.setPosition(w/2,h/2)
        self.window.setDimensions(w*.65, h*.25)
        self.window.draw()

        if self.window.scale[0] >= w*.65 and self.window.scale[1] >= h*.20:
            self.engine.drawText(self.font, "Select the difficulty", (w*.5, h*.65))
            self.menu.render()
            
    def create(self):
        name = string.join(self.name, '')
        family = Family(None)
        family.create(name, self.diffselected)
        self.engine.family = Family(name)
        self.engine.viewport.changeScene("CreateCharacter")
        
    def render(self, visibility):
        w, h = self.engine.w, self.engine.h

        self.engine.drawImage(self.background, scale = (w,h))

        if self.step == 0:
            self.renderNaming()
        elif self.step == 1:
            self.renderDifficulty()
        else:
            self.create()

        if self.error:
            self.engine.showError("You must enter a name")


        
