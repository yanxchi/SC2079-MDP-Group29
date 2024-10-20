import random
import math
import numpy as np
from Algo.path import Path
# Constants
GRID_WIDTH = 20
GRID_HEIGHT = 20
CAR_SIZE = 3  
OBSTACLE_SIZE = 1  # Size of each obstacle (10x10 pixels)
EPSILON = 1e-6  

class Grid:
    def __init__(self, targets, **kwargs) -> None:
        self.grid = [[0 for i in range(GRID_WIDTH)] for j in range(GRID_HEIGHT)]
        self.targets = targets
        self.turning_safe_dist = kwargs.get("turning", 0.5)
        self.straight_safe_dist = kwargs.get("straight", 0.49)
        self.turning_edge_safe_dist = kwargs.get("turning_edge", 0.49)
        self.straight_edge_safe_dist = kwargs.get("straight_edge", 0.49)
    
    def draw_grid(self, car):
        for i in range(GRID_HEIGHT-1,-1,-1):
            for j in range(GRID_WIDTH):
                if (i+0.5,j+0.5) in self.targets:
                    print(self.targets[self.targets.index((i+0.5,j+0.5))], end='')
                elif (i,j) in car.body:
                    print("C", end='')
                elif (i,j) in car.cam:
                    print("O", end='')
                else:
                    print("-", end='')
            print()

    def isvalid(self, y, x, angle):
        maxx, minx = x + max(np.cos(angle)*(self.straight_edge_safe_dist+2), np.cos(angle+np.pi)*(self.straight_edge_safe_dist), np.abs(np.sin(angle)*(self.straight_edge_safe_dist+1))), x-max(np.cos(angle+np.pi)*(self.straight_edge_safe_dist+2), np.cos(angle)*(self.straight_edge_safe_dist), np.abs(np.sin(angle+np.pi)*(self.straight_edge_safe_dist+1)))
        maxy, miny = y + max(np.sin(angle)*(self.straight_edge_safe_dist+2), np.sin(angle+np.pi)*(self.straight_edge_safe_dist), np.abs(np.cos(angle)*(self.straight_edge_safe_dist+1))), y-max(np.sin(angle+np.pi)*(self.straight_edge_safe_dist+2), np.sin(angle)*(self.straight_edge_safe_dist), np.abs(np.cos(angle+np.pi)*(self.straight_edge_safe_dist+1)))
        maxx, minx = max(maxx, minx), min(maxx, minx)
        maxy, miny = max(maxy, miny), min(maxy, miny)
        if(minx<0 or maxx>GRID_WIDTH or miny<0 or maxy>GRID_HEIGHT):
            return False
        
        maxx, minx = x + max(np.cos(angle)*(self.straight_safe_dist+2), np.cos(angle+np.pi)*(self.straight_safe_dist), np.abs(np.sin(angle)*(self.straight_safe_dist+1))), x-max(np.cos(angle+np.pi)*(self.straight_safe_dist+2), np.cos(angle)*(self.straight_safe_dist), np.abs(np.sin(angle+np.pi)*(self.straight_safe_dist+1)))
        maxy, miny = y + max(np.sin(angle)*(self.straight_safe_dist+2), np.sin(angle+np.pi)*(self.straight_safe_dist), np.abs(np.cos(angle)*(self.straight_safe_dist+1))), y-max(np.sin(angle+np.pi)*(self.straight_safe_dist+2), np.sin(angle)*(self.straight_safe_dist), np.abs(np.cos(angle+np.pi)*(self.straight_safe_dist+1)))
        maxx, minx = max(maxx, minx), min(maxx, minx)
        maxy, miny = max(maxy, miny), min(maxy, miny)
        for obstacle in self.targets:
            obsX, obsY = obstacle.x, obstacle.y
            if(obsX >= minx and obsX <= maxx and obsY >= miny and obsY <= maxy):
                return False
        return True
    
    def isvalidturn(self, y, x, angle):
        maxx, minx = x + max(np.cos(angle)*(self.turning_edge_safe_dist+2), np.cos(angle+np.pi)*(self.turning_edge_safe_dist), np.abs(np.sin(angle)*(self.turning_edge_safe_dist+1))), x-max(np.cos(angle+np.pi)*(self.turning_edge_safe_dist+2), np.cos(angle)*(self.turning_edge_safe_dist), np.abs(np.sin(angle+np.pi)*(self.turning_edge_safe_dist+1)))
        maxy, miny = y + max(np.sin(angle)*(self.turning_edge_safe_dist+2), np.sin(angle+np.pi)*(self.turning_edge_safe_dist), np.abs(np.cos(angle)*(self.turning_edge_safe_dist+1))), y-max(np.sin(angle+np.pi)*(self.turning_edge_safe_dist+2), np.sin(angle)*(self.turning_edge_safe_dist), np.abs(np.cos(angle+np.pi)*(self.turning_edge_safe_dist+1)))
        maxx, minx = max(maxx, minx), min(maxx, minx)
        maxy, miny = max(maxy, miny), min(maxy, miny)
        if(minx<0 or maxx>GRID_WIDTH or miny<0 or maxy>GRID_HEIGHT):
            return False
        
        maxx, minx = x + max(np.cos(angle)*(self.turning_safe_dist+2), np.cos(angle+np.pi)*(self.turning_safe_dist), np.abs(np.sin(angle)*(self.turning_safe_dist+1))), x-max(np.cos(angle+np.pi)*(self.turning_safe_dist+2), np.cos(angle)*(self.turning_safe_dist), np.abs(np.sin(angle+np.pi)*(self.turning_safe_dist+1)))
        maxy, miny = y + max(np.sin(angle)*(self.turning_safe_dist+2), np.sin(angle+np.pi)*(self.turning_safe_dist), np.abs(np.cos(angle)*(self.turning_safe_dist+1))), y-max(np.sin(angle+np.pi)*(self.turning_safe_dist+2), np.sin(angle)*(self.turning_safe_dist), np.abs(np.cos(angle+np.pi)*(self.turning_safe_dist+1)))
        maxx, minx = max(maxx, minx), min(maxx, minx)
        maxy, miny = max(maxy, miny), min(maxy, miny)
        for obstacle in self.targets:
            obsX, obsY = obstacle.x, obstacle.y
            if(obsX >= minx and obsX <= maxx and obsY >= miny and obsY <= maxy):
                return False
        return True
        
    def isvalidpath(self, path: Path):
        if path.straight is False:
            for point in path.path_coords:
                if(not self.isvalidturn(point[0], point[1], point[2])):
                    return False
        else:
            for point in path.path_coords:
                if(not self.isvalid(point[0], point[1], point[2])):
                    return False
        return True


def main():
    from entity import Car, Target
    from path import Path
    targetlst = [Target(5,5, "N"), Target(15, 9, "N"), Target(10,1, "N"), Target(15,15, "N")]
    car = Car()
    grid = Grid(targetlst)
    while(True):
        grid.draw_grid(car)
        print(car.angle, car.direction)
        print(car.y, car.x)
        direction = input("Enter direction: ")
        if(direction=="Forward"): car.move(Path((car.y, car.x, car.angle), (car.y+1, car.x, car.angle)), grid)
        else: car.turn(direction, 2, grid)

if __name__ == "__main__":
    main()
