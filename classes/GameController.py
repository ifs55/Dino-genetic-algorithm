"""
Author: Matheus Santos
Description: this class manage the entire game state.
"""
from tkinter import *
from PIL import Image, ImageTk
from classes.CollisionMonitor import ColisionMonitor

class GameController:
    def __init__(self, mode):
        #can be either a train or a game
        self.mode = mode
        self.master = Tk()
        self.canvas = Canvas(self.master, width=800, height=800, bg='#eee')
        self.colisionMonitor = ColisionMonitor(self.master, self.canvas)
    def run(self):
        if(self.mode == "game"):
            self.canvas.pack()
            self.prepareGame()
            mainloop()
    # create game elements
    def prepareGame(self):
        pass