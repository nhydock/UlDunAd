#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
#                                                                   #
# UlDunAd - Ultimate Dungeon Adventure                              #
# Copyright (C) 2009 Blazingamer(n_hydock@comcast.net               #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation; either version 3    #
# of the License, or (at your option) any later version.            #
#                                                                   #
# This program is distributed in the hope that it will be useful,   #
# but WITHOUT ANY WARRANTY; without even the implied warranty of    #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with this program; if not, write to the Free Software       #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,        #
# MA  02110-1301, USA.                                              #
#####################################################################

import GameEngine
import View
from View import *

import random

from Config import Configuration

class Maplist(Layer):
  def __init__(self):
    self.engine = GameEngine
    self.background = self.engine.loadImage(os.path.join("Data", "mapbackground.png"))

    self.button = self.engine.loadImage(os.path.join("Data", "mapmenubutton.png"))
    self.buttonactive = self.engine.loadImage(os.path.join("Data", "mapmenubuttonactive.png"))
    self.menubutton = self.engine.loadImage(os.path.join("Data", "defaultbutton.png"))
    self.menubuttonactive = self.engine.loadImage(os.path.join("Data", "defaultbuttonactive.png"))

    self.maps = self.engine.listpath(os.path.join("Data", "Towns"), "searchfile", "town.ini")
    self.maps.extend(self.engine.listpath(os.path.join("Data", "Towns"), "searchfile", "dungeon.ini"))
    self.formations = self.engine.listpath(os.path.join("Data", "Enemies", "Formations"), "splitfiletype", ".ini")

    self.index = 0

    if self.formations != []:
      self.formation = random.choice(self.formations)

  def update(self):
    self.engine.drawImage(self.background, scale = (640,480))

    if self.index < 0:
      self.index = 0
    if self.index > len(self.maps):
      self.index = len(self.maps) - 7

    maxindex = len(self.maps)
    for i in range(self.index, 7+self.index):
      if i < maxindex:
        active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (320, 70 + (44*(i+1))), scale = (200,32))
        if active == True:
          if flag == True:
            GameEngine.town = str(self.maps[i])
            if os.path.exists(os.path.join("..","Data", "Towns", self.maps[i], "dungeon.ini")):
              from Dungeon import Dungeon
              View.removescene(self)
              View.addscene(Dungeon())
            else:
              from Towns import Towns
              View.removescene(self)
              View.addscene(Towns())
          
        buttonfont = self.engine.renderFont("menu.ttf", self.maps[i], (320, 70+(44*(i+1))), size = 24)

    active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (320, 64), scale = (200,32))
    if active == True:
      if flag == True:
        if self.index + 7 < maxindex:
          self.index += 7
    buttonfont = self.engine.renderFont("menu.ttf", "-UP-", (320, 64), size = 24)

    active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (320, 432), scale = (200,32))
    if active == True:
      if flag == True:
        if self.index - 7 >= 0:
          self.index -= 7
    buttonfont = self.engine.renderFont("menu.ttf", "-DOWN-", (320, 432), size = 24)

    #activate beta battlescene
    if self.formations != []:
      active, flag = self.engine.drawButton(self.menubutton, self.menubuttonactive, coord= (530, 425), scale = (150,45))
      if active == True:
        if flag == True:
          pygame.mixer.music.fadeout(400)
          from BattleScene import BattleScene
          View.removescene(self)
          View.addscene(BattleScene(str(self.formation)))
          from ExtraScenes import LoadingScene
          View.addscene(LoadingScene("Preparing Battle", 4.5))

      buttonfont = self.engine.renderFont("default.ttf", "Random Battle", (530, 425))

    #activate beta menu scene
    active, flag = self.engine.drawButton(self.menubutton, self.menubuttonactive, coord= (110, 425), scale = (150,45))
    if active == True:
      if flag == True:
        from MenuSystem import MenuSystem
        View.removescene(self)
        View.addscene(MenuSystem())
    buttonfont = self.engine.renderFont("default.ttf", "Menu", (110, 425))

  def clearscene(self):
    del  self.background, self.maps, self.menubutton, self.menubuttonactive, self.engine
