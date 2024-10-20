import numpy as np
from Algo.dubins import Dubins
from Algo.astar import astar
from Algo.rrt import rrt
from Algo.hstar import hstar
from Algo.utils import *

def greedy(targets, cur_pos=(0.5,1.5,np.pi/2), env=None, algo_car:Dubins = Dubins, algo_search: rrt = rrt, radius: float = 2):
    mp = {}
    order = []
    path = []
    total_dist = 0
    while len(targets) > 0:
        min_dist = float('inf')
        min_target = None
        min_path = None
        min_loc = None
        for target in targets:
            if mp.get((cur_pos, target.get_pos()), None) == None:
                dist, cur_path, loc = algo_search(cur_pos, target, env=env, algo=algo_car, radius=radius)
            else:
                dist, cur_path, loc = mp[(cur_pos, target.get_pos())]
            if dist < min_dist:
                min_dist = dist
                min_target = target
                min_path = cur_path
                min_loc = loc
        if min_dist == float('inf'):
            return order, path, float('inf')
    
        targets.remove(min_target)
        order.append(min_target)
        path.append(min_path)
        cur_pos = min_loc
        total_dist += min_dist
    return order, path, total_dist


def dp(targets, cur=(0.5,1.5,np.pi/2), order=[], path=[], env=None, algo_car = Dubins, algo_search = rrt, radius=2):
    mp = {}
    dpmp = {}
    misses = {"misses": 0}
    def dpp(targets, cur=cur, order=[], path=[], env=env, algo_car=algo_car, algo_search=algo_search, radius=2):
        cur_r = (round(cur[0]*2)/2, round(cur[1]*2)/2, round_angle(cur[2]))
        if(len(targets) == 1):
            if mp.get((cur_r, targets[0].get_pos()), None) == None:
                dist, cur_path, loc = algo_search(cur, targets[0], env=env, algo=algo_car, radius=radius)
                mp[(cur_r, targets[0].get_pos())] = (dist, cur_path, loc)
                misses["misses"] += 1
                print("misses", misses['misses'])
            else:
                dist, cur_path, loc = mp[(cur_r, targets[0].get_pos())]
            if dist != float('inf'):
                order.append(targets[0])
                path.append(cur_path)
                return dist
            return 600
        cost = float('inf')
        chosen = None
        cur_path = []
        for i in range(len(targets)):
            new_targets = targets[:i] + targets[i+1:]
            target_hash = tuple([target.get_pos() for target in new_targets])
            if mp.get((cur_r, targets[i].get_pos()), None) == None:
                dist, new_path, new_loc = algo_search(cur, targets[i], env=env, algo=algo_car, radius=radius)
                misses["misses"] += 1
                print("misses", misses['misses'])
                mp[(cur_r, targets[i].get_pos())] = (dist, new_path, new_loc)
            else:
                dist, new_path, new_loc = mp[(cur_r, targets[i].get_pos())]

            if dist == float('inf'):
                continue
            
            new_loc_r = (round(new_loc[0]*2)/2, round(new_loc[1]*2)/2, round_angle(new_loc[2]))
            if dpmp.get((target_hash, new_loc_r), None) != None:
                new_cost = dpmp[(target_hash, new_loc_r)]
            else:
                new_cost = dpp(new_targets, new_loc, env=env, algo_car=algo_car, algo_search=algo_search, radius=radius)
                dpmp[(target_hash, new_loc_r)] = new_cost
            if new_cost + dist <= cost:
                cur_path = new_path
                cost = new_cost + dist
                chosen = [new_loc, targets[i], new_targets]
        if chosen == None:
            return float('inf')
        order.append(chosen[1])
        path.append(cur_path)
        dpp(chosen[2], cur=chosen[0], order=order, path=path, env=env, algo_car=algo_car, algo_search=algo_search, radius=radius)

        return cost
    return dpp(targets, cur=cur, order=order, path=path, env=env, algo_car=algo_car, algo_search=algo_search, radius=radius)

def preprocess(start, targets, env, algo_car=Dubins, algo_search=rrt):
    mp = {}
    for target in targets:
        total, path, loc = algo_search(start, target, env=env, algo=algo_car)
        if total != float('inf'):
            mp[(start, target.get_pos())] = (total, path, loc)
        else:
            mp[(start, target.get_pos())] = (float('inf'), [], None)
    print("preprocess1")
    for i in range(len(targets)):
        for j in range(len(targets)):
            if i == j:
                continue
            stop_pos = get_stopping_pos(targets[i])
            for s in stop_pos:
                total, path, loc = algo_search(s, targets[j], env=env, algo=algo_car)
                if total != float('inf'):
                    mp[(s, targets[j].get_pos())] = (total, path, loc)
                else:
                    mp[(s, targets[j].get_pos())] = (float('inf'), [], None)
    print("preprocess2")
    return mp

def get_distance_matrix(start, targets, algo_car, env, radius):
    mp = {}
    for i, target in enumerate(targets):
        loc1, loc2, loc3 = get_stopping_pos(target)
        # total, path = algo_car.compute_shortest_valid_path(start, loc2, env=env, radius=radius)
        total, path, l = astar(start, target, env=env, algo=algo_car, radius=radius)
        if total != float('inf'):
            mp[(start, target.get_pos())] = (total, path, loc2)
        else:
            mp[(start, target.get_pos())] = (float('inf'), [], None)
    
    for i, target_start in enumerate(targets):
        for j, target_end in enumerate(targets):
            if i == j:
                continue
            loc1, loc2, loc3 = get_stopping_pos(target_end)
            s1, s2, s3 = get_stopping_pos(target_start)
            # total, path = algo_car.compute_shortest_valid_path(s2, loc2, env=env, radius=radius)
            if env.isvalid(s2[0], s2[1], s2[2]):
                total, path, l = astar(s2, target_end, env=env, algo=algo_car, radius=radius)
            elif env.isvalid(s1[0], s1[1], s1[2]):
                total, path, l = astar(s1, target_end, env=env, algo=algo_car, radius=radius)
            elif env.isvalid(s3[0], s3[1], s3[2]):
                total, path, l = astar(s3, target_end, env=env, algo=algo_car, radius=radius)
            if total != float('inf'):
                mp[(target_start.get_pos(), target_end.get_pos())] = (total, path, loc2)
            else:
                mp[(target_start.get_pos(), target_end.get_pos())] = (float('inf'), [], None)

    return mp
