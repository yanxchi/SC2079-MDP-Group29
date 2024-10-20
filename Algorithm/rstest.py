from Algo.reeds_shepp import ReedsShepp
from Algo.dubins import Dubins
from Algo.entity import Target, Car
from Algo.sim import Grid
from Algo.utils import *
import numpy as np

targetlst = [Target(17.5, 7.5, "S"), Target(9.5, 5.5, "S"), Target(9.5,12.5, "E"), Target(4.5,15.5, "W"), Target(15.5,15.5, "S")]
targetlst = [Target(2,2,"N")]
env = Grid(targetlst.copy())
car = Car()
out = ReedsShepp().compute_all_paths((5, 5, 0), (15, 15, np.pi/2), turning_radius=2)

i = 1
for l, path in out:
    print(i)
    i+=1
    obstacles = []
    for seg in path:
        print(seg.straight, seg.steering, seg.forward, seg.len, seg.angle)
        print(seg.start)
        print(seg.goal)
        if seg.goal[1]>6 and seg.goal[1]<7:
            print("hi")
        seg.generate_path(line_resolution=0.1)
        obstacles.append(Target(seg.goal[0], seg.goal[1], "N"))
    plot_path(path=path_to_coord(path), start=(5, 5, 0), obstacles=obstacles, goal=(15, 15, np.pi/2))