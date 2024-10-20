import random
import numpy as np
from Algo.entity import Target
from Algo.dubins import Dubins
from Algo.utils import *

def rrt(start, goal: Target, env, algo: Dubins = Dubins, radius: float = 2):
    '''
    :param start: (y,x,theta) tuple
    :param goal: Target object
    :param env: Grid object
    :param algo: Dubins or ReedsShepp
    :return total: total distance of the path
    '''
    # Try direct path first
    s_space = get_stopping_pos(goal)
    s_space = [s_space[1], s_space[2], s_space[0]] # Prefer the middle stopping position
    for s in s_space:
        total, path = algo.compute_shortest_valid_path(start, s, radius, env)
        if total != float("inf"):
            return total, path, s
    
    tree = set()
    tree.add(start)
    xmax, ymax = len(env.grid[0]), len(env.grid)
    mp = {start: (0, [], start)}
    visited = set()
    visited.add(start)

    while True:
        x = random.randint(1, xmax-2)
        x += 0.5
        y = random.randint(1, ymax-2)
        y += 0.5
        theta = random.choice([0, np.pi/2, np.pi, -np.pi/2])
        if (y, x, theta) in visited:
            continue
        visited.add((y, x, theta))

        valid = False
        for node in tree:
            total, path = algo.compute_shortest_valid_path(node, (y, x, theta), radius, env)
            if total == float("inf"):
                continue
            else:
                valid = True
            if (y, x, theta) not in mp or mp[node][0] + total < mp.get((y, x, theta), (1e9, []))[0]:
                mp[(y, x, theta)] = (mp[node][0] + total, mp[node][1] + path, node)
            for goal_loc in get_stopping_pos(goal):
                total, path = algo.compute_shortest_valid_path((y, x, theta), goal_loc, radius, env)
                if total == float("inf"):
                    continue
                else:
                    return (mp[(y, x, theta)][0] + total, mp[(y, x, theta)][1] + path, path[-1].goal)
        
        if len(visited) > 50:
            return float("inf"), [], None
        
        if valid: tree.add((y, x, theta))
    
    return mp[goal]