from Algo.sim import Grid
from Algo.utils import *
import numpy as np

#TODO: Implement a better simulation(pygame, webapp)
def main():
    from Algo.entity import Car, Target
    from Algo.path import Path
    targetlst = [Target(15.5, 7.5, "W"), Target(9.5, 6.5, "S"), Target(9.5,12.5, "E"), Target(5.5,15.5, "W"), Target(15.5,16.5, "S")]

    car = Car()
    grid = Grid(targetlst)
    while(True):
        grid.draw_grid(car)
        print(car.angle, car.direction)
        print(car.y, car.x)
        direction = input("Enter direction: ")
        if(direction=="Forward"): car.move(Path(car.getpos(), len=1), grid)
        if(direction=="Backward"): car.move(Path(car.getpos(), len=-1), grid)
        if(direction=="Left"): car.move(Path(car.getpos(), pivot=get_pivot(car.getpos(), 2, "L"), angle=np.pi/2), grid)
        if(direction=="Right"): car.move(Path(car.getpos(), pivot=get_pivot(car.getpos(), 2, "R"), angle=-np.pi/2), grid)

if __name__ == "__main__":
    main()
