import numpy as np
from typing import Literal
import matplotlib.pyplot as plt
import queue

from Algo.path import Path
from Algo.sim import Grid
from Algo.entity import Target
from Algo.utils import *
  
def heuristics(start, goal, penalty=1):
    loc1, loc2, loc3 = get_stopping_pos(goal)
    # return min(np.sqrt((start[0]*penalty-loc1[0]*penalty)**2+(start[1]*penalty-loc1[1]*penalty)**2),
    #         np.sqrt((start[0]*penalty-loc2[0]*penalty)**2+(start[1]*penalty-loc2[1]*penalty)**2),
    #         np.sqrt((start[0]*penalty-loc3[0]*penalty)**2+(start[1]*penalty-loc3[1]*penalty)**2))
    return min(abs(start[0]-loc1[0])+abs(start[1]-loc1[1]), abs(start[0]-loc2[0])+abs(start[1]-loc2[1]), abs(start[0]-loc3[0])+abs(start[1]-loc3[1]))

def hstar(start: tuple, goal: Target, env, algo=None, radius: float = 2):
    pq = queue.PriorityQueue()
    visited = set()
    loc1, loc2, loc3 = get_stopping_pos(goal)
    mp = {}
    mp[start] = (0, [], start)
    pq.put((0, start))
    print('target',loc1[2])
    print(loc1)
    print(loc2)
    print(loc3)
    miny, maxy = loc1[0], loc3[0]
    minx, maxx = loc1[1], loc3[1]
    if miny>maxy: miny, maxy = maxy, miny
    if minx>maxx: minx, maxx = maxx, minx
    if minx==maxx:
        minx-=1
        maxx+=1
    if miny==maxy:
        miny-=1
        maxy+=1
    minx -= 0.5
    maxx += 0.5
    miny -= 0.5
    maxy += 0.5
    while not pq.empty():
        cost, node = pq.get()
        
        if miny<=node[0]<=maxy and minx<=node[1]<maxx and node[2]==loc2[2]:  
            res = mp[node]
            path = res[1]
            idx = 0
            while idx + 1 < len(path):
                if path[idx].straight and path[idx+1].straight:
                    path[idx] = Path(start=path[idx].start, goal=path[idx+1].goal, len=path[idx].len+path[idx+1].len, forward=path[idx].forward)
                    path[idx].generate_path()
                    path.pop(idx+1)
                else:
                    idx += 1
                    
            return res[0], path, res[2]

        fr = Path(start=node, radius=radius, forward=True, steering="L", angle=np.pi/2, len=np.pi/2 * radius)
        fr.generate_path()
        fr.goal = (round(fr.goal[0], 3), round(fr.goal[1], 3), fr.goal[2])
        if env.isvalidpath(fr) and (mp[node][0] + fr.len + radius) < mp.get(fr.goal, (1e9, []))[0]: 
            mp[fr.goal] = (mp[node][0] + fr.len + radius, mp[node][1]+[fr], fr.goal)
            pq.put((mp[node][0] + fr.len + heuristics(fr.goal, goal), fr.goal))

        fl = Path(start=node, radius=radius, forward=True, steering="R", angle=np.pi/2, len=np.pi/2 * radius)
        fl.generate_path()
        fl.goal = (round(fl.goal[0], 3), round(fl.goal[1], 3), fl.goal[2])
        if env.isvalidpath(fl) and (mp[node][0] + fl.len + radius) < mp.get(fl.goal, (1e9, []))[0]:
            mp[fl.goal] = (mp[node][0] + fl.len + radius, mp[node][1]+[fl], fl.goal)
            pq.put((mp[node][0] + fl.len + heuristics(fl.goal, goal), fl.goal))

        br = Path(start=node, radius=radius, forward=False, steering="R", angle=np.pi/2, len=np.pi/2 * radius)
        br.generate_path()
        br.goal = (round(br.goal[0], 3), round(br.goal[1], 3), br.goal[2])
        if env.isvalidpath(br) and (mp[node][0] + br.len + radius) < mp.get(br.goal, (1e9, []))[0]: 
            mp[br.goal] = (mp[node][0] + br.len + radius, mp[node][1]+[br], br.goal)
            pq.put((mp[node][0] + br.len + heuristics(br.goal, goal), br.goal))

        bl = Path(start=node, radius=radius, forward=False, steering="L", angle=np.pi/2, len=np.pi/2 * radius)
        bl.generate_path()
        bl.goal = (round(bl.goal[0], 3), round(bl.goal[1], 3), bl.goal[2])
        if env.isvalidpath(bl) and (mp[node][0] + bl.len + radius) < mp.get(bl.goal, (1e9, []))[0]: 
            mp[bl.goal] = (mp[node][0] + bl.len + radius, mp[node][1]+[bl], bl.goal)
            pq.put((mp[node][0] + bl.len + heuristics(bl.goal, goal), bl.goal))

        f = Path(start=node, forward=True, len=1)
        f.generate_path()
        f.goal = (round(f.goal[0], 3), round(f.goal[1], 3), f.goal[2])
        if env.isvalidpath(f) and (mp[node][0] + f.len) < mp.get(f.goal, (1e9, []))[0]: 
            mp[f.goal] = (mp[node][0] + f.len + radius, mp[node][1]+[f], f.goal)
            pq.put((mp[node][0] + f.len + heuristics(f.goal, goal), f.goal))

        b = Path(start=node, forward=False, len=1)
        b.generate_path()
        b.goal = (round(b.goal[0], 3), round(b.goal[1], 3), b.goal[2])
        if env.isvalidpath(b) and (mp[node][0] + b.len) < mp.get(b.goal, (1e9, []))[0]: 
            mp[b.goal] = (mp[node][0] + b.len, mp[node][1]+[b], b.goal)
            pq.put((mp[node][0] + b.len + heuristics(b.goal, goal), b.goal))

        visited.add(node)
    return float("inf"), [], None
    


