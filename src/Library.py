#=======================================================#
#
# UlDunAd - Ultimate Dungeon Adventure
# Copyright (C) 2009 Blazingamer/n_hydock@comcast.net
#       http://code.google.com/p/uldunad/
# Licensed under the GNU General Public License V3
#      http://www.gnu.org/licenses/gpl.html
#
#=======================================================#

import Engine
from Engine import GameEngine

from View import *

import Config

import textwrap
import math

import Input

class Library(Layer):
  def __init__(self):

    self.engine = GameEngine()
    self.townname = Engine.town

    self.library = os.path.join("Data", "Places", "Towns", self.townname, "Library")

    self.libraryback = self.engine.loadImage(os.path.join(self.library, "library.png"))
    self.librarian = self.engine.loadImage(os.path.join(self.library, "librarian.png"))
    self.booktex = self.engine.loadImage(os.path.join(self.library, "book.png"))
    self.bookcover = self.engine.loadImage(os.path.join(self.library, "bookcover.png"))

    self.secondarybutton = self.engine.data.secondarybutton
    self.menubutton = self.engine.data.defaultbutton

    self.enterdialog = 0

    self.books = self.engine.listpath(self.library, "splitfiletype", ".txt", "filename")

    self.index = 0
    self.lineindex = 0
    self.spacehit = False
    self.active = False
    self.book = None
    self.booklines = None

  def readbook(self):

    if self.booktex != None:
      self.engine.drawImage(self.booktex)

    book = open(os.path.join("..", self.library, self.book + ".txt"))
    book.seek(0)
    booklines = []
    for line in book.read().splitlines():
      if line == "" or line == "\n":
        booklines.append("")
      else:
        line = textwrap.wrap(line, 60)
        for lines in line:
          booklines.append(lines)

    lines = len(booklines)
    pages = int(math.ceil(lines/25))+1
    currentpage = int(math.ceil((self.lineindex + 1)/25)) + 1

    for i, line in enumerate(booklines):
      if i >= self.lineindex and i < self.lineindex + 25:
        self.engine.renderFont("default.ttf", line, coord = (50, 75 + 15*(i-self.lineindex)), size = 12, alignment = 1, color = (0,0,0))
    self.engine.renderFont("default.ttf", "Page " + str(currentpage) + " of " + str(pages), coord = (435, 465), size = 12, alignment = 2, color = (0,0,0))
    self.engine.renderFont("menu.ttf", str(self.book), coord = (435, 50), size = 18, alignment = 2, color = (0,0,0))


    active, flag = self.engine.drawButton(self.menubutton, coord= (560, 205), scale = (150,45))
    if active == True:
      if flag == True:
        open(os.path.join("..", self.library, self.book + ".txt")).close()
        self.book = None
        self.lineindex = 0
        self.booklines = None
    buttonfont = self.engine.renderFont("default.ttf", "Return", (560, 205))

    active, flag = self.engine.drawButton(self.menubutton, coord= (560, 75), scale = (150,45))
    if active == True:
      if flag == True:
        if self.lineindex + 25 < lines:
          self.lineindex += 25
    buttonfont = self.engine.renderFont("default.ttf", "Next Page", (560, 75))

    active, flag = self.engine.drawButton(self.menubutton, coord= (560, 130), scale = (150,45))
    if active == True:
      if flag == True:
        if self.lineindex - 25 >= 0:
          self.lineindex -= 25
    buttonfont = self.engine.renderFont("default.ttf", "Previous Page", (560, 130))


  def lookatbooks(self):

    self.engine.renderFont("menu.ttf", "Press LEFT or RIGHT to change selected book", (630, 30), size = 18, flags = "Shadow", alignment = 2)

    if self.bookcover != None:
      self.engine.drawImage(self.bookcover, scale = (640,480))

    maxindex = len(self.books)
   
    self.engine.renderFont("menu.ttf", self.books[self.index], (320, 260), size = 18)

    active, flag = self.engine.drawButton(self.menubutton, coord= (110, 425), scale = (150,45))
    if active == True:
      if flag == True:
        self.active = False
    buttonfont = self.engine.renderFont("default.ttf", "Return", (110, 425))

    active, flag = self.engine.drawButton(self.menubutton, coord= (530, 425), scale = (150,45))
    if active == True:
      if flag == True:
        self.book = self.books[self.index]

    buttonfont = self.engine.renderFont("default.ttf", "Read", (530, 425))

  def update(self):
    self.engine.screenfade((0,0,0,255))

    if self.libraryback != None:
      self.engine.drawImage(self.libraryback, scale = (640,480))
    if self.librarian != None:
      self.engine.drawImage(self.librarian, coord = (320,160))
    
    for key, char in Input.getKeyPresses():
      if key == K_SPACE:
        self.spacehit = True
      if self.active == True:
        if key == K_LEFT:
          if self.index - 1 >= 0:
            self.index -= 1
        if key == K_RIGHT:
          maxindex = len(self.books)
          if self.index + 1 < maxindex:
            self.index += 1


    if self.spacehit == True:
      self.enterdialog = 1
      self.spacehit = False

    if self.enterdialog == 0:
      self.engine.renderTextbox("default.ttf", ("Hello, welcome to the library of " + str(self.townname), ""), size = 18)
    elif self.enterdialog == 1 and self.active == False:
      self.engine.renderTextbox("default.ttf", ("We have many books here, which would you like to check out?", ""), size = 18)
      for i, choice in enumerate(["Take a Look", "Leave"]):
        active, flag = self.engine.drawButton(self.secondarybutton, coord= (120, 128 + (26*i)), scale = (220,24))
        if active == True:
          if flag == True:
            if i == 0:
              if self.books != []:
                self.active = True
              else:
                self.enterdialog = 2
            else:
              from Towns import Towns
              self.engine.changescene(self, Towns())

    
        buttonfont = self.engine.renderFont("default.ttf", choice, (120, 128 + (26*i)))


    elif self.enterdialog == 2:
      self.engine.renderTextbox("default.ttf", ("There are no books in this library", ""), size = 18)
    elif self.active == True and self.book == None:
      self.lookatbooks()
    if self.book != None:
      self.readbook()


        
