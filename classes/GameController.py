
from tkinter import Canvas, Tk, mainloop, NW, Label, Frame, W
from PIL import Image, ImageTk
from classes.CollisionMonitor import ColisionMonitor
from classes.Dino import Dino
from classes.Cactus import Cactus
from classes.FlyingDino import FlyingDino
from classes.CollisionMonitor import ColisionMonitor
from classes.ObstacleGenerator import ObstacleGenerator
from classes.DinoBrain import DinoBrain
from utils.draw import draw_nn
import sys
import numpy as np

class GameController:
    def __init__(self, mode, dinos_per_gen = 10):
        #can be either a train or a game
        self.mode = mode
        self.master = Tk()
        self.width = 800
        self.height = 800
        self.canvas = Canvas(self.master, width=800, height=800, bg='#fff')
        self.infoPanel = Frame(self.master, bg='#fff')
        self.colisionMonitor = ColisionMonitor(self.master, self.canvas, self.stopGround)
        self.dinos = []
        self.dinosOnScreen = 0
        self.obstacles = []
        self.colisionMonitor = None
        self.obstacleGenerator = None
        self.initialDinoNum = dinos_per_gen
        self.game_params = {'distance': 100, 'speed': 25, 'height': 0, 'width': 50}
        self.master.bind('<r>', self.restart)
        self.scoresCheckPoint = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 80, 110, 140, 200, 250]
        self.imgs_pil_ground = [
            Image.open("./assets/ground.png"),
            Image.open("./assets/ground-1.png")]
        self.ground = ImageTk.PhotoImage(self.imgs_pil_ground[0])
        self.ground_1 = ImageTk.PhotoImage(self.imgs_pil_ground[1])
        # display image on canvas
        self.ground_id = self.canvas.create_image(0, 695, image=self.ground, anchor=NW)
        self.ground_id_1 = self.canvas.create_image(400, 695, image=self.ground_1, anchor=NW)
        self.ground_id_2 = self.canvas.create_image(800, 695, image=self.ground, anchor=NW)
        self.ground_animation_id = None
        self.interfaceObject = {}
        self.score = 0
        self.record = 0
        try:
            general_data = np.load('data/general/game.npy')
            self.general_record = general_data[0]
        except IOError as err:
            self.general_record = 0
            np.save('data/general/game.npy', np.array([0]))
        
        self.n_generations = 0
        self.game_modes =  {
            "train": "train",
            "game": "game",
            "simulation": "simulation"
        }
        self.nn_elements = {
            'neurons': [],
            'connections': []
        }
    def saveGeneralRecord(self):
        if(self.general_record<=self.score):
            print(self.general_record)
            np.save('data/general/game.npy', np.array([self.general_record]))
    def prepareInterface(self):
        #l1.grid(row = 0, column = 0, sticky = W, pady = 2)
        self.infoPanel.pack(fill='x')
        speedLabel = Label(self.infoPanel, text="Speed: "+str(self.game_params['speed'])+"/"+str(len(self.scoresCheckPoint)), bg='#fff')
        speedLabel.grid(row=0, column=0, pady=10, sticky = W)
        self.interfaceObject['speedLabel'] = speedLabel

        dinosAlive = Label(self.infoPanel, text="Dinos: "+str(self.initialDinoNum), bg='#fff')
        dinosAlive.grid(row=1, column=0, pady=10, sticky = W)
        self.interfaceObject['dinosAlive'] = dinosAlive
        
        scoreLabel = Label(self.infoPanel, text="Score: "+str(self.score), bg='#fff')
        scoreLabel.grid(row=2, column=0, pady=10, sticky = W)
        self.interfaceObject['score'] = scoreLabel
        
        record = Label(self.infoPanel, text="Record: "+str(self.record), bg='#fff')
        record.grid(row=0, column=1, padx=20, pady=10, sticky = W)
        self.interfaceObject['record'] = record
        
        n_generation = Label(self.infoPanel, text="Generation: "+str(self.n_generations), bg='#fff')
        n_generation.grid(row=1, column=1, padx=20, pady=10, sticky = W)
        self.interfaceObject['n_generation'] = n_generation
        
        general_record = Label(self.infoPanel, text="General record: "+str(self.general_record), bg='#fff')
        general_record.grid(row=2, column=1, padx=20, pady=10, sticky = W)
        self.interfaceObject['general_record'] = general_record

        weights = np.load('data/brain/best_w.npy')
        weights_flatten = weights.flatten()
        biases = np.load('data/brain/best_b.npy').flatten()
        self.nn_elements = draw_nn(width=self.width, height = self.height, nn_shape=[5, 2], weights = weights, weights_flatten = weights_flatten,biases = biases,
            canvas = self.canvas, padding=[50, 10, 400, 300], neuron_size=10)
    def animateGround(self):
        self.canvas.move(self.ground_id, -9, 0)
        self.canvas.move(self.ground_id_1, -9, 0)
        self.canvas.move(self.ground_id_2, -9, 0)
        #[left top right bottom]
        if(self.canvas.coords(self.ground_id)[0]<-400):
            self.canvas.move(self.ground_id, 1200, 0)
        if(self.canvas.coords(self.ground_id_1)[0]<-400):
            self.canvas.move(self.ground_id_1, 1200, 0)
        if(self.canvas.coords(self.ground_id_2)[0]<-400):
            self.canvas.move(self.ground_id_2, 1200, 0)
        self.ground_animation_id = self.canvas.after(20, self.animateGround)
    
    def run(self):
        if(self.mode == self.game_modes["game"]):
            self.prepareInterface()
            self.canvas.pack()
            self.prepareGame()
            self.animateGround()
            mainloop()
        elif(self.mode == self.game_modes["train"]):
            self.prepareInterface()
            self.canvas.pack()
            self.prepareTrain()
            self.animateGround()
            mainloop()
        elif(self.mode == self.game_modes["simulation"]):
            self.prepareInterface()
            self.canvas.pack()
            self.prepareSimulation()
            self.animateGround()
            mainloop()
    def decreaseDinos(self):
        self.dinosOnScreen-=1
        self.colisionMonitor.dinosOnScreen = self.dinosOnScreen
        self.updateLabels()

    def updateGameParams(self, distance=None, speed=None, height=None, width=None):
        if(not distance is None):
           self.game_params['distance'] = distance
        if(not speed is None):
           self.game_params['speed'] = speed
        if(not height is None):
           self.game_params['height'] = height 
        if(not width is None):
           self.game_params['width'] = width
        #print(self.game_params)
    def updateLabels(self):
        self.interfaceObject['speedLabel'].config(text="Speed: "+str(25 - self.game_params['speed'])+"/"+str(len(self.scoresCheckPoint)))
        self.interfaceObject['dinosAlive'].config(text="Dinos: "+str(self.dinosOnScreen)+"/"+str(self.initialDinoNum))
        self.interfaceObject['score'].config(text="Score: "+str(self.score))
        self.interfaceObject['record'].config(text="Record: "+str(self.record))
        self.interfaceObject['n_generation'].config(text="Generation: "+str(self.n_generations))
        self.interfaceObject['general_record'].config(text="General record: "+str(self.general_record))
    # create game elements
    def prepareGame(self):
        self.dinos.append(Dino(self.master, self.canvas, DinoBrain(), self.game_params, self.decreaseDinos, mode=self.mode, game_modes=self.game_modes, color="black"))
        self.dinos.append(Dino(self.master, self.canvas, DinoBrain(), self.game_params, self.decreaseDinos, mode="train", game_modes=self.game_modes, color="red"))
        self.dinos[-1].brain.load()
        self.dinosOnScreen = 2
        self.obstacleGenerator = ObstacleGenerator(self.master, self.canvas, self.updateGameParams, self.increaseScore)
        self.obstacleGenerator.updateObstaclesSpeed(self.game_params['speed'])
        self.obstacleGenerator.run()
        self.colisionMonitor = ColisionMonitor(self.master, self.canvas, self.stopGround, self.dinos, self.obstacleGenerator.obstacles, self.dinosOnScreen)
        self.colisionMonitor.run()
    # create train elements
    def prepareTrain(self):
        for i in range(self.initialDinoNum):
            self.dinosOnScreen+=1
            dino = Dino(self.master, self.canvas, DinoBrain(), self.game_params, self.decreaseDinos, mode=self.mode, game_modes=self.game_modes)
            dino.brain.load()
            self.dinos.append(dino)

        for dino in self.dinos[1:]:
            dino.brain.mutate()

        self.obstacleGenerator = ObstacleGenerator(self.master, self.canvas, self.updateGameParams, self.increaseScore)
        self.obstacleGenerator.updateObstaclesSpeed(self.game_params['speed'])
        self.obstacleGenerator.run()
        self.colisionMonitor = ColisionMonitor(self.master, self.canvas, self.stopGround, self.dinos, self.obstacleGenerator.obstacles, self.dinosOnScreen)
        self.colisionMonitor.run()
    # create simulation elements
    def prepareSimulation(self):
        for i in range(self.initialDinoNum):
            self.dinosOnScreen+=1
            dino = Dino(self.master, self.canvas, DinoBrain(), self.game_params, self.decreaseDinos, mode=self.mode, game_modes=self.game_modes)
            self.dinos.append(dino)

        self.obstacleGenerator = ObstacleGenerator(self.master, self.canvas, self.updateGameParams, self.increaseScore)
        self.obstacleGenerator.updateObstaclesSpeed(self.game_params['speed'])
        self.obstacleGenerator.run()
        self.colisionMonitor = ColisionMonitor(self.master, self.canvas, self.stopGround, self.dinos, self.obstacleGenerator.obstacles, self.dinosOnScreen)
        self.colisionMonitor.run()
    def stopGround(self):
        print("New gen")

        if(self.general_record<=self.score):
            self.general_record = self.score
            np.save('data/general/game.npy', np.array([self.general_record]))
        self.n_generations+=1
        if(self.record<self.score):
            self.record = self.score
        self.resetGameParams()
        self.canvas.after_cancel(self.ground_animation_id)
        brain_index = None
        for i, dino in enumerate(self.dinos):
            if(dino.best):
                brain_index = i
                print("best: ", brain_index)
                if(self.mode == "train"):
                    dino.brain.save()
        
        self.obstacleGenerator.updateObstaclesSpeed(self.game_params['speed'])
        self.obstacleGenerator.reset()
       
        for  i, dino in enumerate(self.dinos):
            dino.reset()
            if(i != brain_index):
                dino.setBrain(self.dinos[brain_index].brain.getClone(True))
         
        for  i, dino in enumerate(self.dinos):
            dino.game_params = self.game_params
            dino.animate()
            dino.run()
        self.score = 0

        self.dinosOnScreen = len(self.dinos)
        self.colisionMonitor.dinosOnScreen = self.dinosOnScreen

        self.updateLabels()
        self.animateGround()
        self.colisionMonitor.run()
        self.obstacleGenerator.run()
    def increaseScore(self, score):
        self.score+=score
        if(self.score in self.scoresCheckPoint):
            self.game_params['speed']-=1
            self.obstacleGenerator.updateObstaclesSpeed(self.game_params['speed'])
        if(self.score==350 and self.mode == self.game_modes['train']):
            for dino in self.dinos:
                if(dino.onScreen):
                    dino.brain.save()
        if(self.general_record<self.score):
            self.general_record = self.score
        self.updateLabels()
    def resetGameParams(self):
        self.game_params = {'distance': 100, 'speed': 25, 'height': 0, 'width': 50}
    def restart(self, event):
        for dino in self.dinos:
            dino.reset()
        self.resetGameParams()
        self.animateGround()
        self.obstacleGenerator.reset()
        self.obstacleGenerator.run()
