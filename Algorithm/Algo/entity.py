import random
import math
import numpy as np
from Algo.path import Path

class Car:
    def __init__(self, x=1.5, y=1.5, angle=np.pi/2) -> None:
        # Fix Y as vertical axis and X as horizontal axis
        self.x = x #TODO 
        self.y = y
        self.body = []
        self.cam = []
        self.turning_dist = 2
        self.direction = "N" 
        self.angle = np.pi/2
        self.generate_body()

    def getpos(self):
        return (self.y, self.x, self.angle)

    def generate_body(self):
        # Recalibrate angle range
        if(self.angle>np.pi):
            self.angle -= 2*np.pi
        elif(self.angle<-np.pi):
            self.angle += 2*np.pi
        
        if(self.angle>np.pi/4 and self.angle<=np.pi*3/4):
            self.direction = "N"
        elif(self.angle>np.pi*3/4 or self.angle<=-np.pi*3/4):   
            self.direction = "W"
        elif(self.angle>-np.pi*3/4 and self.angle<=-np.pi*1/4):
            self.direction = "S"
        else:
            self.direction = "E"
        tempX, tempY = np.floor(self.x), np.floor(self.y)
        if(self.direction == "N"):
            self.body = [(tempY-1, tempX-1), (tempY-1, tempX), (tempY-1, tempX+1), 
                         (tempY, tempX-1), (tempY, tempX), (tempY, tempX+1), 
                         (tempY+1, tempX-1), (tempY+1, tempX+1)]
            self.cam = [(tempY+1, tempX)]
        elif(self.direction == "S"):
            self.body = [(tempY-1, tempX-1), (tempY-1, tempX+1), 
                         (tempY, tempX-1), (tempY, tempX), (tempY, tempX+1), 
                         (tempY+1, tempX-1), (tempY+1, tempX), (tempY+1, tempX+1)]
            self.cam = [(tempY-1, tempX)]
        elif(self.direction == "E"):
            self.body = [(tempY-1, tempX-1), (tempY-1, tempX), (tempY-1, tempX+1), 
                         (tempY, tempX-1), (tempY, tempX), 
                         (tempY+1, tempX-1), (tempY+1, tempX), (tempY+1, tempX+1)]
            self.cam = [(tempY, tempX+1)]
        elif(self.direction == "W"):
            self.body = [(tempY-1, tempX-1), (tempY-1, tempX), (tempY-1, tempX+1),
                         (tempY, tempX), (tempY, tempX+1), 
                         (tempY+1, tempX-1), (tempY+1, tempX), (tempY+1, tempX+1)]
            self.cam = [(tempY, tempX-1)]
    
    def move(self, path: Path, env):
        if path.straight is False:
            for point in path.path:
                if(not env.isvalidturn(point[0], point[1])):
                    return False
        else:
            for point in path.path:
                if(not env.isvalid(point[0], point[1])):
                    return False
        self.y, self.x, self.angle = path.path[-1]
        self.generate_body()
        return True

    def turn(self, direction, distance, env):
        initx, inity, initangle = self.x, self.y, self.angle
        if direction == "Left":
            if self.direction == "N":
                pivot = (self.y-distance, self.x)
                quadrant = "NE"
                self.y += distance
                self.x -= distance
                self.angle = (self.angle + 90) % 360
            elif self.direction == "S":
                pivot = (self.y+distance, self.x)
                quadrant = "SW"
                self.y -= distance
                self.x += distance
                self.angle = (self.angle + 90) % 360
            elif self.direction == "E":
                pivot = (self.y, self.x+distance)
                quadrant = "SE"
                self.y += distance
                self.x += distance
                self.angle = (self.angle + 90) % 360
            elif self.direction == "W":
                pivot = (self.y, self.x-distance)
                quadrant = "NW"
                self.y -= distance
                self.x -= distance
                self.angle = (self.angle + 90) % 360
        elif direction == "Right":
            if self.direction == "N":
                pivot = (self.y+distance, self.x)
                quadrant = "NW"
                self.y += distance
                self.x += distance
                self.angle = (self.angle - 90) % 360
            elif self.direction == "S":
                pivot = (self.y-distance, self.x)
                quadrant = "SE"
                self.y -= distance
                self.x -= distance
                self.angle = (self.angle - 90) % 360
            elif self.direction == "E":
                pivot = (self.y, self.x-distance)
                quadrant = "NE"
                self.y -= distance
                self.x += distance
                self.angle = (self.angle - 90) % 360
            elif self.direction == "W":
                pivot = (self.y, self.x+distance)
                quadrant = "SW"
                self.y += distance
                self.x -= distance
                self.angle = (self.angle - 90) % 360
        if(not env.isvalidturn((pivot[0]+0.5, pivot[1]+0.5), quadrant, max(0, distance-1.5), distance+1.5)):
            self.x = initx
            self.y = inity
            self.angle = initangle
            return False
        if(not env.isvalid(self.x, self.y)):
            self.x = initx
            self.y = inity
            self.angle = initangle
            return False
        self.generate_body()
        return True
    
class Target:
    def __init__(self, y, x, direction, id=None) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.id = id
        if self.direction == "N":
            self.angle = np.pi/2
        elif self.direction == "S":
            self.angle = -np.pi/2
        elif self.direction == "E":
            self.angle = 0
        elif self.direction == "W":
            self.angle = np.pi
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, tuple):
            return self.x == value[1] and self.y == value[0]
        return self.x == value.x and self.y == value.y

    def __str__(self) -> str:
        if self.direction == "N":
            return "⬆️"
        elif self.direction == "S":
            return "⬇️"
        elif self.direction == "E":
            return "➡️"
        elif self.direction == "W":
            return "⬅️"

    def get_pos(self):
        return (self.y, self.x, self.angle)