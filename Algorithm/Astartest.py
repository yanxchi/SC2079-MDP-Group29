from Algo.sim import Grid
from Algo.utils import *
from Algo.astar import astar
from Algo.rrt import rrt
from Algo.dubins import Dubins
from Algo.reeds_shepp import ReedsShepp
import numpy as np
import time


def main():
    from Algo.entity import Car, Target
    from Algo.path import Path
    targetlst = [Target(15.5, 7.5, "W"), Target(9.5, 6.5, "S"), Target(9.5,12.5, "E"), Target(5.5,15.5, "W"), Target(16.5,15.5, "S")]
    # targetlst = [Target(9.5,10.5, "E")]
    car = Car()
    grid = Grid(targetlst)
    time1 = time.time()
    start = (12.5, 15.5, np.pi/2)
    for target in targetlst:
        total, path, loc = astar(get_stopping_pos(target)[1], targetlst[2], grid, algo=ReedsShepp)
        print("out")
        print(total, path, loc)
        plot_path(obstacles=targetlst, path=path_to_coord(path), start=get_stopping_pos(target)[1])

    # total, path, loc = rrt((12.5, 15.5, np.pi/2), targetlst[2], grid)
    time2 = time.time()
    print(time2-time1)
    print(total, path, loc)
    plot_path(obstacles=targetlst, path=path_to_coord(path), start=start)
    

if __name__ == "__main__":
    main()