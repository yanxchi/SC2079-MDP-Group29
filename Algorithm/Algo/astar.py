import queue
import numpy as np

from Algo.path import Path
from Algo.entity import Target
from Algo.dubins import Dubins
from Algo.utils import *

def heuristics(start, goal: Target, penalty=1):
    loc1, loc2, loc3 = get_stopping_pos(goal)
    # return min(np.sqrt((start[0]*penalty-loc1[0]*penalty)**2+(start[1]*penalty-loc1[1]*penalty)**2),
    #            np.sqrt((start[0]*penalty-loc2[0]*penalty)**2+(start[1]*penalty-loc2[1]*penalty)**2),
    #            np.sqrt((start[0]*penalty-loc3[0]*penalty)**2+(start[1]*penalty-loc3[1]*penalty)**2))
    return min(abs(start[0]-loc1[0])+abs(start[1]-loc1[1]), abs(start[0]-loc2[0])+abs(start[1]-loc2[1]), abs(start[0]-loc3[0])+abs(start[1]-loc3[1]))

def astar(start: tuple, goal: Target, env, algo: Dubins = Dubins, radius: float = 2):
    '''
    :param start: (y,x,theta) tuple
    :param goal: Target object
    :param env: Grid object
    :param algo: Dubins or ReedsShepp
    :return total: total distance of the path
    :return path: list of Path segments
    :return goal_loc: (y,x,theta) tuple, the final position
    '''
    pq = queue.PriorityQueue()
    visited = set()
    loc1, loc2, loc3 = get_stopping_pos(goal)
    if goal.get_pos()[0]==10.5 and goal.get_pos()[1]==11.5:
        print(loc1, loc2, loc3)
    total, path, end = algo.compute_shortest_valid_path(start, loc2, radius, env)
    if total != float("inf"): return total, path, end
    total, path, end = algo.compute_shortest_valid_path(start, loc1, radius, env)
    if total != float("inf"): return total, path, end
    total, path, end = algo.compute_shortest_valid_path(start, loc3, radius, env)
    if total != float("inf"): return total, path, end

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
    minx, maxx = max(0.49, minx), min(19.6, maxx)
    miny, maxy = max(0.49, miny), min(19.6, maxy)

    mp = {}
    pq.put((0, start))
    mp[start] = (0, [], start)
    while not pq.empty():
        cost, node = pq.get()
        if miny<=node[0]<=maxy and minx<=node[1]<=maxx and node[2]==loc2[2]:  
            print(len(visited))
            return mp[node]
        check_val = (round(node[0]*2)/2, round(node[1]*2)/2, round_angle(node[2]))
        if check_val in visited:
            continue

        for loc in [loc2, loc1, loc3]:
            total, path, end = algo.compute_shortest_isvalid_path(node, loc, radius, env)
            if total != float("inf"):
                print(len(visited))
                mp[loc] = (mp[node][0] + total, mp[node][1] + path, end)
                pq.put((mp[node][0] + total, loc))
                # return mp[node][0] + total, mp[node][1] + path, end
                break
        if total == float("inf"):
            fr = Path(start=node, radius=radius, forward=True, steering="L", angle=np.pi/2, len=np.pi/2 * radius)
            fr.generate_path()
            if env.isvalidpath(fr) and (mp[node][0] + fr.len + radius) < mp.get(fr.goal, (1e9, []))[0]: 
                mp[fr.goal] = (mp[node][0] + fr.len + radius, mp[node][1]+[fr], fr.goal)
                pq.put((mp[node][0] + fr.len + heuristics(fr.goal, goal), fr.goal))

            fl = Path(start=node, radius=radius, forward=True, steering="R", angle=np.pi/2, len=np.pi/2 * radius)
            fl.generate_path()
            if env.isvalidpath(fl) and (mp[node][0] + fl.len + radius) < mp.get(fl.goal, (1e9, []))[0]:
                mp[fl.goal] = (mp[node][0] + fl.len + radius, mp[node][1]+[fl], fl.goal)
                pq.put((mp[node][0] + fl.len + heuristics(fl.goal, goal), fl.goal))

            br = Path(start=node, radius=radius, forward=False, steering="R", angle=np.pi/2, len=np.pi/2 * radius)
            br.generate_path()
            if env.isvalidpath(br) and (mp[node][0] + br.len + radius) < mp.get(br.goal, (1e9, []))[0]: 
                mp[br.goal] = (mp[node][0] + br.len + radius, mp[node][1]+[br], br.goal)
                pq.put((mp[node][0] + br.len + heuristics(br.goal, goal), br.goal))

            bl = Path(start=node, radius=radius, forward=False, steering="L", angle=np.pi/2, len=np.pi/2 * radius)
            bl.generate_path()
            if env.isvalidpath(bl) and (mp[node][0] + bl.len + radius) < mp.get(bl.goal, (1e9, []))[0]: 
                mp[bl.goal] = (mp[node][0] + bl.len + radius, mp[node][1]+[bl], bl.goal)
                pq.put((mp[node][0] + bl.len + heuristics(bl.goal, goal), bl.goal))

            f = Path(start=node, forward=True, len=1)
            f.generate_path()
            if env.isvalidpath(f) and (mp[node][0] + f.len) < mp.get(f.goal, (1e9, []))[0]: 
                mp[f.goal] = (mp[node][0] + f.len, mp[node][1]+[f], f.goal)
                pq.put((mp[node][0] + f.len + heuristics(f.goal, goal), f.goal))

            b = Path(start=node, forward=False, len=1)
            b.generate_path()
            if env.isvalidpath(b) and (mp[node][0] + b.len) < mp.get(b.goal, (1e9, []))[0]: 
                mp[b.goal] = (mp[node][0] + b.len, mp[node][1]+[b], b.goal)
                pq.put((mp[node][0] + b.len + heuristics(b.goal, goal), b.goal))

        check_val = (round(node[0]*2)/2, round(node[1]*2)/2, round_angle(node[2]))
        visited.add(check_val)
        if len(visited) > 120:
            print(start, goal.get_pos())
            return float("inf"), [], None
    return float("inf"), [], None