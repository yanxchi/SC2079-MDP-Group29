from Algo.hamiltonian import greedy, dp, get_distance_matrix
from Algo.dubins import Dubins
from Algo.reeds_shepp import ReedsShepp
from Algo.entity import Target
from Algo.sim import Grid
from Algo.astar import astar
from Algo.rrt import rrt
from Algo.hstar import hstar
from Algo.path import Path
from Algo.utils import *
import numpy as np
import time

CAR_START = (0.5, 0, np.pi/2)
CAR_END = (2.5, 0, -np.pi/2)

def write_path(path):
    ss = ""
    for p in path:
        print(p)
        for pseg in p:
            print(pseg)
            for coords in pseg.path_coords:
                ss += f"{coords[0]:.8f} {coords[1]:.8f} {coords[2]:.8f}\n"
    
    return ss

def write_stm(path, order):
    ss = ""
    for id, p in enumerate(path):
        for pseg in p:
            if pseg.forward and pseg.straight:
                ss += f"nw{round(pseg.len*20)%350:0>3}\n"
            elif pseg.forward and not pseg.straight and pseg.steering=="R":
                ss += f"ne{round(pseg.angle/np.pi * 180)%360:0>3}\n"
            elif pseg.forward and not pseg.straight and pseg.steering=="L":
                ss += f"nw{round(pseg.angle/np.pi * 180)%360:0>3}\n"
            elif not pseg.forward and pseg.straight:
                ss += f"nx{round(pseg.len*20)%360:0>3}\n"
            elif not pseg.forward and not pseg.straight and pseg.steering=="R":
                ss += f"nc{round(pseg.angle/np.pi * 180)%360:0>3}\n"
            elif not pseg.forward and not pseg.straight and pseg.steering=="L":
                ss += f"nz{round(pseg.angle/np.pi * 180)%360:0>3}\n"
        ss += f"snap {order[id].id}\n"
    return ss

def main():
    targetlst = [Target(8.5, 0.5, "E", 1), Target(6.5, 6.5, "S", 2), Target(17.5, 6.5, "W", 3),Target(9.5, 10.5, "N", 4),Target(6.5, 14.5, "E", 5), Target(13.5, 14.5, "N", 6), Target(0.5, 19.5, "W", 7)]

    target2 = targetlst.copy()
    env = Grid(targetlst.copy(), turning=1.2, straight=0.8)
    order = []
    path = []
    time1 = time.time()

    dist = dp(targetlst, env=env, order=order, path=path, algo_car=ReedsShepp, algo_search=astar, radius=2.4)

    print("length" , dist*10)
    time2 = time.time()
    print("time taken:", time2-time1)

    # ----------------------------------------------------SIMULATOR CODE----------------------------------------------------------------

    # #directory of res/raw of android studio project folder
    # save_directory = r"C:\Y3 S1\SC2079 - Multidisciplinary Design Project\Android Code\app\src\main\res\raw" #replace path as needed
    # if not os.path.exists(save_directory):
    #     os.makedirs(save_directory)

    # #writing path coordinates to path.txt in res/raw in android studio project folder
    # for p in path:
    #     for coords in p.path_coords:
    #         ss += f"{coords[0]:.8f} {coords[1]:.8f} {coords[2]:.8f}\n"

    # file_path = os.path.join(save_directory, "path.txt")

    # with open(file_path, "w") as f:
    #     f.write(ss)

    # #writing obstacle info to obstacle.txt in res/raw in android studio project folder
    # obstacles_file_path = os.path.join(save_directory, "obstacles.txt")
    # with open(obstacles_file_path, "w") as f:
    #     for target in targetlst:
    #         y_coord = int(target.y)  #rounded down to the nearest whole number
    #         x_coord = int(target.x)
    #         direction = ""

    #         if target.direction == "N":
    #             direction = "NORTH"
    #         elif target.direction == "S":
    #             direction = "SOUTH"
    #         elif target.direction == "E":
    #             direction = "EAST"
    #         elif target.direction == "W":
    #             direction = "WEST"

    #         #file format: ycoord xcoord dir
    #         f.write(f"{y_coord} {x_coord} {direction}\n")

# ----------------------------------------------------SIMULATOR CODE----------------------------------------------------------------
                

    for entity in order:
        print(entity.id)
    plot_path(obstacles=target2, path=path_to_coord(path), start=(0.5, 1.5, np.pi/2))

if __name__ == "__main__": 
    #Debug code
    main()