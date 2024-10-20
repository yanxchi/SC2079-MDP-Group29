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
    # targetlst = [Target(17.5, 7.5, "S"), Target(9.5, 5.5, "S"), Target(9.5,12.5, "E"), Target(4.5,15.5, "W"), Target(15.5,15.5, "S")]
    # targetlst = [Target(19.5, 0.5, "S", 1), Target(9.5, 4.5, "S", 2), Target(0.5,10.5, "W", 3), Target(0.5,15.5, "N", 4), Target(7.5,19.5, "W", 5), Target(10.5, 13.5, "S", 6),Target(13.5, 10.5, "E", 7), Target(13.5,18.5,"N",8)]
    # targetlst = [Target(10.5, 5.5, "S", 1), Target(10.5, 7.5, "S", 2), Target(10.5, 9.5, "S", 3), Target(10.5, 11.5, "S", 4), Target(10.5, 13.5, "S", 5), Target(10.5,15.5, "S", 6), Target(10.5, 17.5, "S", 7), Target(18.5, 18.5, "W", 8)]
    targetlst = [Target(8.5, 0.5, "E", 1), Target(6.5, 6.5, "S", 2), Target(17.5, 6.5, "W", 3),Target(9.5, 10.5, "N", 4),Target(6.5, 14.5, "E", 5), Target(13.5, 14.5, "N", 6), Target(0.5, 19.5, "W", 7)]
    # targetlst = [Target(18.5, 1.5, "S", 1), Target(12.5, 6.5, "N", 2), Target(7.5, 10.5, "E", 3),Target(16.5, 15.5, "S", 4),Target(9.5, 19.5, "W", 5), Target(2.5, 13.5, "W", 6)]
    # targetlst = [Target(15.5,18.5, "N", 1)]
    # targetlst = [Target(15.5, 1.5, 'S', 1)]
    # targetlst = [Target(19.5, 0.5, "S", 1), Target(8.5, 8.5, "N", 2)]
    # targetlst.append(Target(0.5, 19.5, "S"), Target(19.5, 0.5, "N")) # 2 Dudsu0
    target2 = targetlst.copy()
    env = Grid(targetlst.copy(), turning=1.2, straight=0.8)
    order = []
    path = []
    time1 = time.time()
    # order, path, dist = greedy(targetlst, env=env, algo_car=ReedsShepp, algo_search=hstar, radius=2.5)
    # #p1
    # # dist, path = Dubins.rsl((-11.5, 10.5, np.pi/2), (0.5, 12.5, np.pi/2), get_pivot((-11.5, 10.5, np.pi/2), 2.4, "R"), get_pivot((0.5, 12.5, np.pi/2), 2.4, "L"), 2.4)
    # dist, path = ReedsShepp.compute_shortest_path((-11.5, 10.5, np.pi/2), (0.5, 12.5, np.pi/2), 2.4)
    # patht += path
    # #p2
    # # dist, path = Dubins.rsl((0.5, 12.5, np.pi/2), (6.5, 18.5, np.pi/2), get_pivot((0.5, 12.5, np.pi/2), 2.4, "R"), get_pivot((6.5, 18.5, np.pi/2), 2.4, "L"), 2.4)
    # dist, path = ReedsShepp.compute_shortest_path((0.5, 12.5, np.pi/2), (6.5, 18.5, np.pi/2), 2.4)
    # patht += path
    # patht += [Path(start=(6.5, 18.5, np.pi/2), len=1, forward=True)]
    # # dist, path = Dubins.lsl((7.5, 18.5, np.pi/2), (7.5, 2.5, -np.pi/2), get_pivot((7.5, 18.5, np.pi/2), 2.4, "L"), get_pivot((7.5, 2.5, -np.pi/2), 2.4, "L"), 2.4)
    # dist, path = ReedsShepp.compute_shortest_path((7.5, 18.5, np.pi/2), (7.5, 2.5, -np.pi/2), 2.4)
    # patht += path
    # patht += [Path(start=(7.5, 2.5, -np.pi/2), len=1, forward=True)]
    # # dist, path = Dubins.lsr((6.5, 2.5, -np.pi/2), (-6.5, 10.5, -np.pi/2), get_pivot((6.5, 2.5, -np.pi/2), 2.4, "L"), get_pivot((-6.5, 10.5, -np.pi/2), 2.4, "R"), 2.4)
    # dist, path = ReedsShepp.compute_shortest_path((6.5, 2.5, -np.pi/2), (-11.5, 10.5, -np.pi/2), 2.4)
    # patht += path
    # patht = [patht]
    # print(patht)
    # dist, path = Dubins.lsr(CAR_START, (CAR_START[0]+(301/100), CAR_START[1]-1.5, CAR_START[2]), get_pivot(CAR_START, 1, "L"), get_pivot((CAR_START[0]+(301/100), CAR_START[1]-1.5, CAR_START[2]), 1, "R"), 1)
    # path = [path]
    dist = dp(targetlst, env=env, order=order, path=path, algo_car=ReedsShepp, algo_search=astar, radius=2.4)
    # dist, path, _ = astar((0.5,1.5,np.pi/2), targetlst[-1], env, ReedsShepp, 2.5)
    # mp = get_distance_matrix((0.5,1.5,np.pi/2), targetlst, ReedsShepp, env, 2.4)
    # paths = [p[1] for p in paths]
    # for key, value in mp.items():
    #     print(key, value[0])
    #     if value[0] == float('inf'):
    #         print("No path found")
    #     else:
    #         plot_path(obstacles=target2, path=path_to_coord([value[1]]), start=(1.5, 1.5, np.pi/2))
    # pl=[]
    # straight_edge_safe_dist = 0.49
    # for p in path:
    #     for pseg in p:
    #         for coords in pseg.path_coords:
    #             y, x, angle = coords
    #             print(angle)
    #             tr = (2.5*np.sin(angle-0.54)+0*np.cos(angle-0.54)+y, 2.5*np.cos(angle-0.54)-0*np.sin(angle-0.54)+x)
    #             tl = (2.5*np.sin(angle+0.54)+0*np.cos(angle+0.54)+y, 2.5*np.cos(angle+0.54)-0*np.sin(angle+0.54)+x)
    #             br = (2.5*np.sin(angle+0.54-3.14)+0*np.cos(angle+0.54-3.14)+y, 2.5*np.cos(angle+0.54-3.14)-0*np.sin(angle+0.54-3.14)+x)
    #             bl = (2.5*np.sin(angle-0.54+3.14)+0*np.cos(angle-0.54+3.14)+y, 2.5*np.cos(angle-0.54+3.14)-0*np.sin(angle-0.54+3.14)+x)
    #             maxx, minx = x + np.cos(angle)*(straight_edge_safe_dist+2) + np.sin(angle)*(straight_edge_safe_dist+1), x+np.cos(-angle) * (straight_edge_safe_dist) + np.sin(-angle) * (straight_edge_safe_dist+1)
    #             maxy, miny = y + np.sin(angle)*(straight_edge_safe_dist+2) + np.cos(angle)*(straight_edge_safe_dist+1), y+np.sin(-angle) * straight_edge_safe_dist + np.cos(-angle) * straight_edge_safe_dist
    #             maxx, minx = max(maxx, minx), min(maxx, minx)
    #             maxy, miny = max(maxy, miny), min(maxy, miny)
    #             pl.append(bl)
    #             pl.append(tr)
    #             pl.append(br)
    #             pl.append(tl)

    #     #plot points in pl with matplotlib
    # plot_path(obstacles=target2, path=pl, start=(1.5, 1.5, np.pi/2))


    print("length" , dist*10)
    time2 = time.time()
    print("time taken:", time2-time1)

    # path += [mp[(0.5,1.5,np.pi/2), targetlst[0].get_pos()][1]]
    # for i in range(len(targetlst)-1):
    #     path += [mp[(targetlst[i].get_pos(), targetlst[i+1].get_pos())][1]]
    
    # for p in path:
    #     for pseg in p:
    #         pseg.generate_path()

    # write_path("path.txt", path)
    # print(write_stm(path, order))
    # with open("path_stm.txt", "w") as f:
    #     f.write(write_stm(path, order))

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
    main()