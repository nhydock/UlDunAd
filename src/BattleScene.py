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

from GameEngine import *

from Player import Player

from View import *
import os

from sys import *

from Enemy import Enemy

import math
import random

from Config import *
import pygame

class BattleScene(Layer):
  def __init__(self, formation):

    self.engine = GameEngine
    self.party = []
    self.partyko = []
    for partymember in self.engine.party:
      self.party.append(Player(partymember))
    
    self.formation = formation
    self.formationini = Configuration(os.path.join("..", "Data", "Enemies", "Formations", self.formation)).formation
    self.enemies = self.formationini.enemies.split(", ")  
    self.enemy = []
    self.enemyko = []
    for enemy in self.enemies:
      self.enemy.append(Enemy(enemy))

    self.enemysprite = []
    for enemy in self.enemy:
      self.enemysprite.append(self.engine.loadImage(os.path.join("Data",  "Enemies", "Graphics", enemy.image)))

    self.formationdiv = self.formationini.coord.split(";")
    self.formationcoord = []
    for i in range(len(self.formationdiv)):
      self.formationcoord.append(self.formationdiv[i].split(", "))

    self.formationscale = self.formationini.scale.split(";")

    self.engine.inbattle = False
    if os.path.exists(os.path.join("..", "Data", "Audio", "Battle")):
      self.engine.inbattle = True
      songs = self.engine.listpath(os.path.join("Data", "Audio", "Battle"), "splitfiletype", "audio")
      self.audio = Sound().loadAudio(random.choice(songs))
    else:
      if os.path.isfile(os.path.join("Data", "Audio", "battle.mp3")):
        self.audio = Sound().loadAudio("battle.mp3")
      else:
        self.audio = None

    Sound().volume(float(self.engine.battlevolume)/10)

    terrain = self.formationini.terrain

    try:
      self.background = self.engine.loadImage(os.path.join("Data", "Terrains", terrain + ".png"), returnnone = False)
    except:
      self.background = self.engine.loadImage(os.path.join("Data", "Terrains", terrain + ".jpg"), returnnone = True)

    self.hue = None
    if os.path.isfile(os.path.join("Data", "Terrains", terrain + ".ini")):
      terrainini = Configuration(os.path.join("Data", "Terrains", terrain + ".ini")).terrain
      self.hue = terrainini.__getattr__("hue").split(",")

    self.button = self.engine.loadImage(os.path.join("Data", "battlebutton.png"))
    self.buttonactive = self.engine.loadImage(os.path.join("Data", "battlebuttonactive.png"))

    self.atb = self.engine.loadImage(os.path.join("Data", "atb.png"))
    self.atbback = self.engine.loadImage(os.path.join("Data", "atbback.png"))

    self.hpbar = self.engine.loadImage(os.path.join("Data", "hpbar.png"))
    self.hpback = self.engine.loadImage(os.path.join("Data", "hpbarback.png"))

    self.hud = self.engine.loadImage(os.path.join("Data", "battlehud.png"))
    self.hudhighlight = self.engine.loadImage(os.path.join("Data", "battlehighlight.png"))
    self.hudhighlightactive = self.engine.loadImage(os.path.join("Data", "battlehighlightactive.png"))

    self.attackcb = self.engine.loadImage(os.path.join("Data", "battlecirclebottom.png"))
    self.attackct = self.engine.loadImage(os.path.join("Data", "battlecircletop.png"))

    self.enemynamebar = self.engine.loadImage(os.path.join("Data", "enemynamebar.png"))

    self.battle = False

    self.playercommand = 0
    self.enemycommand = 1

    self.displaydamage = 0
    self.timer = 0.0
    self.rotatestart = 0
    self.fade = False
    self.stop = False
    self.spacehit = False
    self.defend = False
    self.attackboost = 0

    self.barframe = 1

    self.activemember = None
    self.activeenemy = None

    self.roll = 1
    self.playertargeted = 0
    self.playertarget = 0

    self.multiplier = 100.0
    self.bonusbar = self.engine.loadImage(os.path.join("Data", "bonusbar.png"))
    self.bonusbarfill = self.engine.loadImage(os.path.join("Data", "bonusbarfill.png"))
    self.bonusbarback = self.engine.loadImage(os.path.join("Data", "bonusbarback.png"))
    self.selectingspell = False
    self.selectingenemy = False
    self.selectingitem = False
    self.index = 0

    GameEngine.resetKeyPresses()

  def showspells(self, partymember):

    commands = self.party[partymember].spells

    maxindex = len(commands)

    for i in range(self.index, 4+self.index):
      if i < maxindex:
        active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (550, 365 + (25*(i-self.index))), scale = (160,25), activeshift = -15)        
        if active == True:
          buttonfont = self.engine.renderFont("default.ttf", commands[i], (535, 365 + (25*(i-self.index))))
          if flag == True:
            self.spell = commands[i] + ".ini"
            self.spellini = Configuration(os.path.join("..", "Data", "Spells", self.spell)).spell
            if self.party[partymember].currentsp < int(self.spellini.cost): #if player sp is less than the cost of the spell then stop the command
              return
            else:
              self.spellanimation = self.engine.loadImage(os.path.join("Data", "Animations", self.spellini.animation))
              self.spelldamage = int(self.spellini.damage) + random.randint(0, int(self.spellini.variance)) + random.randint(0, self.party[partymember].mag)
              self.selectingenemy = True
        else:
          buttonfont = self.engine.renderFont("default.ttf", commands[i], (550, 365 + (25*i)))

    active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (550, 340), scale = (160,25), activeshift = -15)        
    if active == True:
      buttonfont = self.engine.renderFont("default.ttf", "Return", (535, 340))
      if flag == True:
        self.selectingspell = False
    else:
      buttonfont = self.engine.renderFont("default.ttf", "Return", (550, 340))

  def showitems(self, partymember):

    commands = self.party[partymember].inventory

    maxindex = len(commands)

    for i in range(self.index, 4+self.index):
      if i < maxindex:
        name = Configuration(os.path.join("..", "Data", "Items", commands[i] + ".ini")).item.__getattr__("name")
        active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (550, 365 + (25*(i-self.index))), scale = (160,25), activeshift = -15)        
        if active == True:
          buttonfont = self.engine.renderFont("default.ttf", name, (535, 365 + (25*(i-self.index))))
          if flag == True:
            self.item = commands[i] + ".ini"
            self.itemini = Configuration(os.path.join("..", "Data", "Items", self.item)).item
            self.itemfunction = self.itemini.function.split(".")
            if self.itemfunction[0] == "Heal":
              self.battlecommand(3, partymember, playertarget = None)
            elif self.itemfunction[0] == "Damage":
              self.selectingenemy = True
        else:
          buttonfont = self.engine.renderFont("default.ttf", name, (550, 365 + (25*(i-self.index))))

    active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (550, 340), scale = (160,25), activeshift = -15)        
    if active == True:
      buttonfont = self.engine.renderFont("default.ttf", "Return", (535, 340))
      if flag == True:
        self.selectingitem = False
    else:
      buttonfont = self.engine.renderFont("default.ttf", "Return", (550, 340))

  def battlecommand(self, i, partymember = 0, playertarget = 0):
    self.playercommand = i + 1

    self.selectingspell = False      
    self.battle = True
    self.roll = 1
    self.timer = 0
    self.displaydamage = 0
    self.stop = False

    self.party[partymember].defending = False
    self.playertarget = playertarget

    if i == 0 or i == 1:
      self.rotatestart = random.randint(0, 359)
    elif i == 1:
      self.attackboost = random.randint(0, self.party[partymember].atk)
    elif i == 3:
      if self.itemfunction[0] == "Damage":
        self.attackboost = random.randint(0, int(int(self.itemfunction[2])/5))

  def enemybattlecommand(self, i):
    self.battle = True
    self.roll = 0
    self.displaydamage = 0
    self.activeenemy = i
    self.playertargeted = random.randint(0, len(self.party)-1)
    self.attackboost = random.randint(0, self.enemy[self.activeenemy].atk)

  def fight(self, playercommand, enemycommand, roll, partymember = None):
    if roll == 0:
      if self.enemycommand == 1:
        self.attack(0, partymember)

    if roll == 1:
      if self.playercommand == 1 or self.playercommand == 2:
        self.renderbattlecircle(self.activemember)
      elif self.playercommand == 3:
        self.castspell(self.activemember)
      elif self.playercommand == 4:
        if self.itemfunction[0] == "Heal":
          self.displayturn(int(self.itemfunction[2]), 1, self.activemember)
        else:
          self.displayturn(int(self.itemfunction[2]) + self.attackboost, 1, self.activemember)


  def castspell(self, partymember):
    speed = 60/float(self.spellini.frames)
    if self.stop == False:
      if self.timer <= float(self.spellini.frames):
        self.timer += (float(self.spellini.frames)/speed)
        self.engine.drawImage(self.spellanimation, (int(self.formationcoord[self.playertarget][0]), int(self.formationcoord[self.playertarget][1])), frames = int(self.spellini.frames), currentframe = self.timer, direction = self.spellini.direction)
      else:
        self.stop = True
    else:
      self.timer = 0
      self.displayturn(self.spelldamage, 1, partymember)

  def renderbattlecircle(self, partymember):
    if self.stop == False:
      var = random.randint(30,90)
      self.engine.renderFont("default.ttf", "Press Space to Stop", (320, 64), size = 24)
      if self.playercommand == 1: 
        self.engine.renderFont("default.ttf", "Attack", (320, 96), size = 24) 
      elif self.playercommand == 2:
        self.engine.renderFont("default.ttf", "Defend", (320, 96), size = 24) 
    else:
      var = 0
    self.timer += var
    time = math.radians(self.timer/4)
    rotate = self.rotatestart + ((self.timer/7))
    timer = float(1800 - self.timer)
    if timer <= 0.0 or self.spacehit == True:
      self.stop = True
      if int(timer) in range(600, 900):
        if self.playercommand == 1:
          self.attack(1, self.activemember)
        else:
          self.party[partymember].defending = True
          self.spacehit = False
          self.clearvariables(self.playercommand)
      else:
        self.displayturn("Miss", 1, partymember)
    else:
      if self.playercommand == 1:
        self.engine.drawImage(self.attackcb, (float(int(self.formationcoord[self.playertarget][0])), float(int(self.formationcoord[self.playertarget][1]))), scale = (150,150))
        self.engine.drawImage(self.attackct, (float(int(self.formationcoord[self.playertarget][0])), float(int(self.formationcoord[self.playertarget][1]))), scale = (150*(timer/900.0),150*(timer/900.0)), rot = -rotate)
      else:
        self.engine.drawImage(self.attackcb, (320, 240), scale = (150,150))
        self.engine.drawImage(self.attackct, (320, 240), scale = (150*(timer/900.0),150*(timer/900.0)), rot = -rotate)

  def attack(self, who, partymember):
    if who == 0:
      if self.party[partymember].defending == True:
        damage = (self.enemy[self.activeenemy].atk*3 + self.attackboost)/(self.party[partymember].defn*2)
      else:
        damage = (self.enemy[self.activeenemy].atk*3 + self.attackboost)/self.party[partymember].defn
    elif who == 1:
      damage = (self.party[partymember].atk*3 + self.attackboost)/self.enemy[self.playertarget].defn

    self.displayturn(damage, who, partymember)

  def displayturn(self, damage, who, partymember):
    self.displaydamage = self.displaydamage + 20
    if who == 1:
      self.engine.screenfade((0,0,0,255-(self.displaydamage*2)))
      if self.playercommand == 4:
        if self.itemfunction[0] == "Heal":
          self.engine.renderFont("default.ttf", str(damage), (450 + (self.displaydamage/20), 380+(partymember*30)), size = 18, flags = "Shadow", color = (0, 255, 0))
        elif self.itemfunction[0] == "Damage":
          self.engine.renderFont("default.ttf", str(damage), (int(self.formationcoord[self.playertarget][0]) - (self.displaydamage/20), int(self.formationcoord[self.playertarget][1])), size = 24, flags = "Shadow")
      else:
        self.engine.renderFont("default.ttf", str(damage), (int(self.formationcoord[self.playertarget][0]) - (self.displaydamage/20), int(self.formationcoord[self.playertarget][1])), size = 24, flags = "Shadow")
        if self.playercommand == 3:
          self.engine.renderFont("default.ttf", self.spellini.cost, (450 + (self.displaydamage/20), 380+(partymember*30)), size = 18, flags = "Shadow")

    else:
      self.engine.renderFont("default.ttf", str(damage), (450 + (self.displaydamage/20), 380+(partymember*30)), size = 16, flags = "Shadow")

    if self.displaydamage >= 500:
      if damage == "Miss":
        damage = 0
      if who == 0:
        self.party[partymember].currenthp -= damage
      else:
        if self.playercommand == 4:
          if self.itemfunction[0] == "Heal":
            if self.itemfunction[1] == "HP":
              self.party[partymember].currenthp += damage
            elif self.itemfunction[1] == "SP":
              self.party[partymember].currentsp += damage
          elif self.itemfunction[0] == "Damage":
            if self.itemfunction[1] == "HP":
              self.enemy[self.playertarget].currenthp -= damage
            elif self.itemfunction[1] == "SP":
              self.enemy[self.playertarget].currentsp -= damage
        else:
          self.enemy[self.playertarget].currenthp -= damage
          if self.playercommand == 3:
            self.party[partymember].currentsp -= int(self.spellini.cost)
      self.displaydamage = 0
      self.spacehit = False

      self.clearvariables(self.playercommand)

  def clearvariables(self, i):
    self.battle = False
    self.stop = True
    self.timer = 0
    self.displaydamage = 0

    if self.roll == 1:
      self.selectingitem = False
      self.selectingspell = False

    if i == 1 or i == 2:
      self.rotatestart = 0
      self.spacehit = False
      if i == 2:
        self.defend = False
    if i == 3:
      self.spell = None
      self.spellini = None
      self.spellanimation = None
      self.spelldamage = None
    if i == 4:
      if self.roll == 1:
        self.party[self.activemember].inventory.remove(self.item.split(".ini")[0])
      self.item = None
      self.itemini = None
      self.itemanimation = None
      self.itemfunction = None

    if self.roll == 0:
      self.enemy[self.activeenemy].currentatb = 0
    else:
      self.party[self.activemember].currentatb = 0
      self.activemember = None
      self.playertarget = None
      self.selectingenemy = False
            

  def updateATB(self):
    for i, player in enumerate(self.party):
      if player.currentatb <= 300:
        if (self.activemember == None and self.engine.battlemode == "wait") or self.engine.battlemode == "active":
          div = random.randint(4, 7)
          if player.currentatb < 300 and player not in self.partyko:
            player.currentatb += (player.spd/div)
          elif player in self.partyko:
            player.currentatb = 0
          if self.multiplier > 0.0:
            self.multiplier -= 0.05
      if player.currentatb >= 300:
        if self.activemember == None:
          player.currentatb = 300
          self.activemember = i
      if self.activemember == i and player in self.partyko:
        self.activemember = None

    for i, enemy in enumerate(self.enemy):
      if enemy.currentatb < 300 and enemy not in self.enemyko:
        if (self.activemember == None and self.engine.battlemode == "wait") or self.engine.battlemode == "active":
          div = random.randint(4, 7)
          enemy.currentatb += (enemy.spd/div)
      elif enemy.currentatb >= 300:
        if enemy not in self.enemyko:
          if self.party[self.playertargeted] not in self.partyko:
            self.enemybattlecommand(i)
        else:
          enemy.currentatb = 0

  def update(self):

    if self.background != None:
      self.engine.drawImage(self.background, scale = (640,480))
    if self.fade == True:
      self.engine.screenfade((0,0,0,175))

    for i, enemy in enumerate(self.enemy):
      if enemy not in self.enemyko:
        self.engine.drawImage(self.enemysprite[i], coord = (float(int(self.formationcoord[i][0])), float(int(self.formationcoord[i][1]))), scaleper = int(self.formationscale[i]))
      if enemy.currenthp <= 0:
        if enemy not in self.enemyko:
          self.enemyko.append(enemy)


    if self.hue != None:
      self.engine.screenfade((int(self.hue[0]),int(self.hue[1]),int(self.hue[2]),50))

    self.engine.drawImage(self.hud, (225,500), scale = (450, 280))

    self.engine.drawImage(self.bonusbarback, (50, 208), scale = (30,245))
    self.engine.drawBar(self.bonusbarfill, (50, 328), scale = (30,245), barcrop = (float(self.multiplier)/float(100.0)), direction = "Horizontal")
    self.engine.drawImage(self.bonusbar, (50, 195), scale = (100,290))

    for i, player in enumerate(self.party):
      if player.currenthp <= 0:
        player.currenthp = 0

      if self.activemember == i:
        self.engine.drawImage(self.hudhighlightactive, (225,383+(i*30)), scale = (450, 28))
      else:
        self.engine.drawImage(self.hudhighlight, (225,383+(i*30)), scale = (450, 28))

      self.engine.drawBar(self.atbback, (10, 390+(i*30)), scale = (200,6))
      self.engine.drawBar(self.atb, (10, 390+(i*30)), scale = (200,6), barcrop = (float(player.currentatb)/int(300)))

      self.engine.drawBar(self.hpback, (335, 390+(i*30)), scale = (95,6))
      self.engine.drawBar(self.hpbar, (335, 390+(i*30)), scale = (95,180), barcrop = (float(player.currentsp)/int(player.sp)), frames = 30, currentframe = self.barframe)

      self.engine.drawBar(self.hpback, (215, 390+(i*30)), scale = (115,6))
      self.engine.drawBar(self.hpbar, (215, 390+(i*30)), scale = (115,180), barcrop = (float(player.currenthp)/int(player.hp)), frames = 30, currentframe = self.barframe)

      self.engine.renderFont("default.ttf", str(player.currenthp) + "/" + str(player.hp), (330, 380+(i*30)), size = 18, flags = "Shadow", alignment = 2)
      self.engine.renderFont("default.ttf", "HP", (215, 380+(i*30)), size = 18, flags = "Shadow", alignment = 1)

      self.engine.renderFont("default.ttf", str(player.currentsp) + "/" + str(player.sp), (430, 380+(i*30)), size = 18, flags = "Shadow", alignment = 2)
      self.engine.renderFont("default.ttf", "SP", (335, 380+(i*30)), size = 18, flags = "Shadow", alignment = 1)

      if player.knockedout == True:
        self.engine.renderFont("default.ttf", str(player.name), (10, 380+(i*30)), size = 18, flags = "Shadow", alignment = 1, color = (255,0,0))
      else:
        self.engine.renderFont("default.ttf", str(player.name), (10, 380+(i*30)), size = 18, flags = "Shadow", alignment = 1)

      if player.currenthp == 0:
        player.knockedout = True
        if player not in self.partyko:
          self.partyko.append(player)
            
    if len(self.party) == len(self.partyko):
      for player in self.party:
        player.playerini.player.__setattr__("currenthp", int(1))
        player.knockedout = False
        player.playerini.player.__setattr__("currentsp", player.currentsp)
        player.playerini.player.__setattr__("monsterskilled", player.monsterskilled + 1)
        player.playerini.save()
      from Maplist import Maplist
      View.removescene(self)
      View.addscene(Maplist())

    for key, char in GameEngine.getKeyPresses():
      if key == K_SPACE and self.battle == True:
        self.spacehit = True
      if key == K_LEFT and (self.selectingitem == True or self.selectingspell == True):
        if self.index - 5 > 0:
          self.index -= 5
      if key == K_RIGHT and (self.selectingitem == True or self.selectingspell == True):
        if self.selectingitem == True:
          maxindex = len(self.party[self.activemember].inventory)
        elif self.selectingspell == True:
          maxindex = len(self.party[self.activemember].spells)
        if self.index + 5 < maxindex:
          self.index += 5


    commands = ["Attack", "Defend", "Skills", "Item", "Flee"]
    if self.battle == False:
      if self.barframe < 30:
        self.barframe += .5
      else:
        self.barframe = 1

      self.updateATB()
      if not len(self.enemy) == len(self.enemyko):
        self.fade = False
        if self.activemember != None and self.selectingspell == False and self.selectingenemy == False and self.selectingitem == False:
          for i, choice in enumerate(commands):
            active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (550, 365 + (25*i)), scale = (160,25), activeshift = -15)
            if active == True:
              buttonfont = self.engine.renderFont("default.ttf", choice, (535, 365 + (25*i)))
              if flag == True: 
                if i == 0:
                  self.selectingenemy = True
                elif i == 1:
                  self.battlecommand(1, self.activemember)
                elif i == 2:
                  if self.party[self.activemember].spells != "None":
                    self.selectingspell = True
                    self.index = 0
                elif i == 3:
                  if self.party[self.activemember].inventory != "None":
                    self.selectingitem = True
                    self.index = 0
                elif i == 4:
                  self.endscene("flee")
            else:
              buttonfont = self.engine.renderFont("default.ttf", choice, (550, 365 + (25*i)))
        elif self.activemember != None and self.selectingspell == True and self.selectingenemy == False:
          self.showspells(self.activemember)
        elif self.activemember != None and self.selectingitem == True and self.selectingenemy == False:
          self.showitems(self.activemember)
        elif self.activemember != None and self.selectingenemy == True:
          for i, enemy in enumerate(self.enemy):
            if enemy not in self.enemyko:
              sprite = self.engine.drawImage(self.enemysprite[i], coord = (float(int(self.formationcoord[i][0])), float(int(self.formationcoord[i][1]))), scaleper = int(self.formationscale[i]), blit = False)
              active, flag = self.engine.mousecol(sprite)
              if active == True:
                self.engine.drawImage(self.enemynamebar, (320, 32), scale = (640, 64))
                self.engine.renderFont("default.ttf", enemy.name, (320, 32), size = 18)
                if flag == True:
                  if self.selectingspell == True:
                    self.battlecommand(2, self.activemember, i)
                  elif self.selectingitem == True:
                    self.battlecommand(3, self.activemember, i)
                  else:
                    self.battlecommand(0, self.activemember, i)
      else:
        self.endscene("victory")
    else:
      self.fade = True
      if self.roll == 1:
        self.fight(self.playercommand, self.enemycommand, self.roll, self.activemember)
      else:
        self.fight(self.playercommand, self.enemycommand, self.roll, self.playertargeted)

  def endscene(self, condition):
    for player in self.party:
      if player.knockedout == True:
        player.playerini.player.__setattr__("currenthp", int(1))
        player.knockedout = False
      else:
        player.playerini.player.__setattr__("currenthp", player.currenthp)
      player.playerini.player.__setattr__("currentsp", player.currentsp)
      player.playerini.player.__setattr__("inventory", ", ".join(player.inventory))

    if condition == "victory":
      for player in self.party:
        player.playerini.player.__setattr__("monsterskilled", player.monsterskilled + 1)
        player.playerini.save()
      View.removescene(self)
      View.addscene(VictoryScene(75.0 + self.multiplier, self.formation))

    elif condition == "flee":
      for player in self.party:
        player.playerini.save()
      self.engine.inbattle = False
      pygame.mixer.music.fadeout(400)
      if self.engine.town != None:
        if self.engine.cells == None:
          from Towns import Towns
          View.removescene(self)
          View.addscene(Towns())
        else:
          from Dungeon import Dungeon
          View.removescene(self)
          View.addscene(Dungeon())
      else:
        from Maplist import Maplist
        View.removescene(self)
        View.addscene(Maplist())
      GameEngine.enemy = None

  def clearscene(self):

    del self.displaydamage, self.timer, self.rotatestart, self.fade, self.stop, self.spacehit
    del self.attackcb, self.attackct, self.battle, self.playercommand, self.enemycommand
    del self.button, self.buttonactive, self.hpbar, self.hpback, self.atb, self.atbback, self.background
    del self.audio, self.party, self.enemy, self.engine

class VictoryScene(Layer):
  def __init__(self, multiplier, formation):

    self.engine = GameEngine
    self.party = []
    self.levelup = []
    for i, partymember in enumerate(self.engine.party):
      self.party.append(Player(partymember))
      self.levelup.append("False")


    self.enemies = Configuration(os.path.join("..", "Data", "Enemies", "Formations", formation)).formation.enemies.split(", ")  
    self.enemy = []
    self.enemyko = []
    for enemy in self.enemies:
      self.enemy.append(Enemy(str(enemy)))

    self.items = []
    for i, enemy in enumerate(self.enemy):
      if enemy.loot != None and enemy.lootchances != None:
        for i, item in enumerate(enemy.loot):
          chance = random.randint(0, 100)
          if chance >= 0 and chance <= int(enemy.lootchances[i]):
            self.items.append(item)

    self.expbar = self.engine.loadImage(os.path.join("Data", "expbar.png"))
    self.barback = self.engine.loadImage(os.path.join("Data", "barback.png"))

    self.background = self.engine.loadImage(os.path.join("Data", "victorybackground.png"))
    self.statusbox = self.engine.loadImage(os.path.join("Data", "victorystatusbox.png"))

    self.button = self.engine.loadImage(os.path.join("Data", "defaultbutton.png"))
    self.buttonactive = self.engine.loadImage(os.path.join("Data", "defaultbuttonactive.png"))

    self.secondarybutton = self.engine.loadImage(os.path.join("Data", "secondarymenubutton.png"))
    self.secondarybuttonactive = self.engine.loadImage(os.path.join("Data", "secondarymenubuttonactive.png"))

    self.enemyexp = 0
    self.enemyavglvl = 0
    for enemy in self.enemy:
      self.enemyexp += int((enemy.exp/len(self.party))*(multiplier/100))

    self.countdownexp = False
    self.finishupcounting = False
    self.finished = False

    self.notokay = False

    GameEngine.resetKeyPresses()

  def update(self):
    for key, char in GameEngine.getKeyPresses():
      if key == K_SPACE:
        if self.countdownexp == False:
          self.countdownexp = True
        elif self.countdownexp == True and self.enemyexp > 0:
          self.finishupcounting = True

    self.engine.drawImage(self.background, scale = (640,480))
    
    if self.countdownexp == True and self.enemyexp == 0:  
      active, flag = self.engine.drawButton(self.button, self.buttonactive, coord= (530, 425), scale = (150,45))
      if flag == True:
        self.finished = True
      self.engine.renderFont("default.ttf", "Finished", (530, 425))

    self.engine.renderFont("menu.ttf", "Loot and Drops", (20, 96), size = 28, flags = "Shadow", alignment = 1)
    for i, item in enumerate(self.items):
      itemini = Configuration(os.path.join("..", "Data", "Items", item+".ini")).item
      self.engine.renderFont("default.ttf", itemini.__getattr__("name"), (20, 128+24*i), size = 20, flags = "Shadow", alignment = 1)

    self.engine.renderFont("menu.ttf", "Status", (620, 70), size = 32, flags = "Shadow", alignment = 2)

    for i, player in enumerate(self.party):

      self.engine.drawImage(self.statusbox, coord = ((640-150), 130+(i*100)), scale = (345, 80))

      self.engine.renderFont("default.ttf", str(player.name), (350, 110+(i*100)), size = 20, flags = "Shadow", alignment = 1)
      self.engine.renderFont("default.ttf", "Lvl:" + str(player.lvl), (620, 110 + (i*100)), size = 20, flags = "Shadow", alignment = 2)

      self.engine.renderFont("default.ttf", str(player.exp) + "/" + str(player.explvl), (620, 140 + (i*100)), size = 16, flags = "Shadow", alignment = 2)
      self.engine.renderFont("default.ttf", str(self.enemyexp), (350, 140 + (i*100)), size = 24, flags = "Shadow", alignment = 1)


      self.engine.drawBar(self.barback, (350, 155 + (i*100)), scale = (260,15))
      self.engine.drawBar(self.expbar, (350, 155 + (i*100)), scale = ((float(player.exp)/float(player.explvl))*260,5))

      if self.countdownexp == True:
        if self.enemyexp > 0:
          if self.finishupcounting == True:
            playerexp += self.enemyexp
          else:
            player.exp += 1
        else:
          self.enemyexp = 0
          self.countdown = False

    
      if player.exp >= player.explvl:
        self.levelup[i] = "True"
      
      if self.levelup[i] == "True":
        self.engine.renderFont("default.ttf", "Level Up!", (480, 155 + (i*100)), size = 30)
        if player.exp >= player.explvl:
          player.exp = player.exp - player.explvl

    if self.countdownexp == True:
      if self.enemyexp > 0:
        if self.finishupcounting == True:
          self.enemyexp = 0
        else:
          self.enemyexp -= 1
      else:
        self.enemyexp = 0
        self.countdown = False

    if self.finished == True:
      for i, player in enumerate(self.party):
        if self.levelup[i] == "True":
          player.lvl += 1
          player.currenthp = player.hp
          player.currentsp = player.sp        
          player.playerini.player.__setattr__("lvl", player.lvl)
          player.playerini.player.__setattr__("currenthp", player.currenthp)
          player.playerini.player.__setattr__("currenthp", player.currentsp)
          self.levelup[i] = "False"
        for item in self.items:
          if i == 0:
            if len(player.inventory) < 20:
              player.inventory.append(item)
            elif len(player.inventory) >= 20 and i+1 < len(self.party):
              self.party[i+1].inventory.append(item)
          if i+1 >= len(self.party) and len(player.inventory) >= 20:
            self.notokay = True

      if self.notokay == True:
        self.engine.screenfade((0,0,0,120))

        active, flag = self.engine.drawButton(self.secondarybutton, self.secondarybuttonactive, coord= (320, 280), scale = (100,48))
        if active == True:
          if flag == True:
            self.notokay = False

        buttonfont = self.engine.renderFont("default.ttf", "OK", (320, 280), size = 16)
        self.engine.renderMultipleFont("default.ttf", ("Your inventory is full!", "Some items were not picked up"), (320, 212), size = 20, flags = "Shadow")

      else:
        self.engine.inbattle = False
        pygame.mixer.music.fadeout(400)
        for player in self.party:
          player.playerini.player.__setattr__("inventory", ", ".join(player.inventory))
          player.playerini.player.__setattr__("exp", player.exp)
          player.playerini.save()
          player.knockedout = False

        if self.engine.town != None:
          if self.engine.cells == None:
            from Towns import Towns
            View.removescene(self)
            View.addscene(Towns())
          else:
            from Dungeon import Dungeon
            View.removescene(self)
            View.addscene(Dungeon())
            self.engine.currentcell += 1
        else:
          from Maplist import Maplist
          View.removescene(self)
          View.addscene(Maplist())

  def clearscene(self):
    del self.levelup, self.finished, self.finishupcounting, self.countdownexp
    del self.enemyexp, self.background, self.barback, self.expbar, self.engine
