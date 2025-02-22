
from tkinter import NW
from PIL import Image, ImageTk
from classes.DinoBrain import DinoBrain
import pickle
import numpy as np
import random

class Dino:
    def __init__(self, master, canvas, brain, game_params, decreaseDinos,jump_height=100, mode="game", game_modes={}, color=None):
        self.master = master
        self.canvas = canvas
        self.jump_height = jump_height
        self.moving = False
        self.bent = False
        self.distance = 0
        self.moving_id = None
        self.moving_bent_id = None
        self.die_id = None
        self.onScreen = True
        self.run_id = None
        self.animation_raise_id  = None
        self.move_factor = {'x': 100, 'y': 650}
        self.brain = brain
        self.game_params = game_params
        self.brain.jumpAction = self.jump_brain_call
        self.brain.bendAction = self.down
        self.decreaseDinos = decreaseDinos
        self.mode = mode
        self.game_modes = game_modes
        self.best = False
        if(color is None):
            self.color = ['black', 'green', 'blue', 'red', 'yellow', 'orange'][random.randint(0, 5)]
        else:
            self.color = color
        # load default image
        self.imgs_pil_bent_running = [
            Image.open("./assets/dino-down-"+self.color+".png"),
            Image.open("./assets/dino-down-1-"+self.color+".png")]
        self.img_pil_bent = self.imgs_pil_bent_running[0]
        self.current_pil_bent_running_index = 0 
        self.img_pil_default = Image.open("./assets/dino-"+self.color+".png")
        self.imgs_pil_running = [
            Image.open("./assets/dino-"+self.color+".png"),
            Image.open("./assets/dino-1-"+self.color+".png"),
            Image.open("./assets/dino-2-"+self.color+".png")]
        self.current_pil_running_index = 0    
        self.image = ImageTk.PhotoImage(self.img_pil_default)
        # display image on canvas
        self.id = self.canvas.create_image(100, 650, image=self.image, anchor=NW)
        #load mask
        self.mask_bent = pickle.load( open( "./data/mask/dino_down_mask", "rb" ) )
        self.mask_default = pickle.load( open( "./data/mask/dino_mask", "rb" ) )
        self.mask = self.mask_default
        if(self.mode == "game"):
            import keyboard
            self.master.bind('<Up>', self.jump_call)
            # keyboard events
            keyboard.on_release_key('down', self.raiseDino)
            keyboard.on_press_key('down', self.down)
        self.animate()
        self.run()
    """ def __del__(self):
        print("deleted") """
    def setBrain(self, brain):
        self.brain = brain
        self.brain.jumpAction = self.jump_brain_call
        self.brain.bendAction = self.down
    def die(self):
        self.decreaseDinos()
        if(self.moving_id):
            self.canvas.after_cancel(self.moving_id)
        if(self.moving_bent_id):
            self.canvas.after_cancel(self.moving_bent_id)
        if(self.animation_raise_id):
            self.canvas.after_cancel(self.animation_raise_id)
        self.onScreen = False
        self.quitAnimation()
    def quitAnimation(self):
        if(self.getBox()[0]>-50):
            self.move(-9)
            self.die_id = self.canvas.after(20, self.quitAnimation)
        else:
            self.onScreen = False
            #print("deleted")
    def animate(self):
        if(not self.moving):
            if(not self.bent):
                self.animation_raise_id = self.canvas.after(130, self.changeRaiseImage)
            else:
                self.moving_bent_id = self.canvas.after(200, self.changeBentImage)
    def run(self):
        if((self.mode == self.game_modes['train'] or self.mode == self.game_modes['simulation'])  and self.onScreen):
            #print(self.game_params)
            self.brain.takeAction(self.prepareInput())
        self.run_id = self.canvas.after(2, self.run)
    def prepareInput(self):
        #print(self.game_params)
        return np.array([
                [
                    self.game_params['height'],
                    self.getYpos(),
                    self.game_params['width'],
                    self.game_params['speed'],
                    self.game_params['distance']
                ]
            ])
    def changeRaiseImage(self):
        if(not self.bent):
            self.current_pil_running_index+=1
            if(self.current_pil_running_index>2):
                self.current_pil_running_index = 0
            self.image = ImageTk.PhotoImage(self.imgs_pil_running[self.current_pil_running_index])
            self.canvas.itemconfig(self.id, image = self.image)
        self.animate()
    def changeBentImage(self):
        if(self.bent):
            self.current_pil_bent_running_index+=1
            if(self.current_pil_bent_running_index>1):
                self.current_pil_bent_running_index = 0
            self.image = ImageTk.PhotoImage(self.imgs_pil_bent_running[self.current_pil_bent_running_index])
            self.canvas.itemconfig(self.id, image = self.image)
        self.animate()
    def jump_call(self, event):
        if(not self.moving):
            self.raiseDino(None)
            self.moving = True
            self.jump(event)

    def jump_brain_call(self, event):
        if(not self.moving):
            self.raiseDino(None)
            self.moving = True
            self.jump(event)
    def jump(self, event):
        if(self.distance<self.jump_height):
            self.distance+=2
            self.move(0, -2)
            self.moving_id = self.canvas.after(3, self.jump, event)
        elif(self.distance>=self.jump_height and self.canvas.coords(self.id)[-1]<650):
            self.distance+=1
            self.move(0, 1)
            self.moving_id = self.canvas.after(3, self.jump, event)
        else:
            self.distance = 0
            self.moving = False
            self.animate()
    def getYpos(self):
        if(self.canvas.coords(self.id)[-1]):
            return 700 - self.canvas.coords(self.id)[-1]
        return 700
    def move(self, x=0, y=0):
        self.canvas.move(self.id, x, y)
        self.move_factor['x']+=x
        self.move_factor['y']+=y
        
    def down(self, event):
        if(self.moving):
            self.distance = self.jump_height
            self.distance+=1
            self.move(0, 2)
        else:
            if(not self.bent):
                self.mask = self.mask_bent
                self.image = ImageTk.PhotoImage(self.img_pil_bent)
                self.canvas.itemconfig(self.id, image = self.image)
                self.move(0, 20)
                self.bent = True

    def raiseDino(self, event):
        if(self.bent):
            self.mask = self.mask_default
            self.move(0, -20)
            self.image = ImageTk.PhotoImage(self.img_pil_default)
            self.canvas.itemconfig(self.id, image = self.image)
            self.bent = False
            self.moving_bent_id = None
            self.animate()

    def getColisionInfo(self):
        # [left, top, right, bottom]
        block_coords = self.canvas.bbox(self.id)

        # the radius at the x axis
        radius_block_x = abs(block_coords[0] - block_coords[2])/2
        
        # the x coord of the middle point
        block_center_x = radius_block_x + block_coords[0]
        
        # the radius at the y axis
        radius_block_y = abs(block_coords[1] - block_coords[3])/2
        # the y coord of the middle point
        block_center_y = radius_block_y + block_coords[1]

        return {'radius_x': radius_block_x, 'radius_y': radius_block_y, 'coords': {'x': block_center_x, 'y': block_center_y}}

    def getBox(self):
         block_coords = self.canvas.bbox(self.id)
         return block_coords

    def reset(self):
        if(self.run_id):
            self.canvas.after_cancel(self.run_id)
        if(self.moving_bent_id):
            self.canvas.after_cancel(self.moving_bent_id)
        if(self.moving_id):
            self.canvas.after_cancel(self.moving_id)
        if(self.die_id):
            self.canvas.after_cancel(self.die_id)
        if(self.animation_raise_id):
            self.canvas.after_cancel(self.animation_raise_id)
        self.canvas.delete(self.id)
        self.image = ImageTk.PhotoImage(self.imgs_pil_running[0])
        self.id = self.canvas.create_image(100, 650, image=self.image, anchor=NW)
        self.mask = self.mask_default
        self.move_factor = {'x': 100, 'y': 650}
        self.bent = False
        self.best = False
        self.moving = False
        self.distance = 0
        #coords = self.canvas.coords(self.id)
        self.onScreen = True

    def pixelInMask(self, pixel, move_factor):
        image_length = len(self.mask)
        init = 0
        end = image_length
        while True:
            i = int((end-init)/2) + init
            # binary search
            #if the mask pixel has the same X axis
            if(self.mask[i]['x']+self.move_factor['x'] == pixel['x']+move_factor['x']):
                back_count = 0
                while self.mask[i-back_count]['x']+self.move_factor['x'] == pixel['x']+move_factor['x']:
                    back_count+=1
                back_count-=1
                # sequential search
                while (i-back_count)>-1 and (i-back_count)<image_length and self.mask[i-back_count]['x']+self.move_factor['x'] == pixel['x']+move_factor['x']:
                    if(self.mask[i-back_count]['y']+self.move_factor['y'] == pixel['y']+move_factor['y']):
                        return True
                    i+=1
                return False
            # if the current mask pixel has a greater X axis, ignore the right side
            elif(self.mask[i]['x']+self.move_factor['x'] > pixel['x']+move_factor['x']):
                end = i
            else:
                # else ignore the right side
                init = i + 1
            # if the pixel with the same X axis wasn't found
            if (end-init)<=0:
                return False
    def getClone(self, mutate=False):
        brain = self.brain.getClone()
        if(mutate):
            brain.mutate()
        return Dino(self.master, self.canvas, brain)
