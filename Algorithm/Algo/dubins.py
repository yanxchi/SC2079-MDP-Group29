import numpy as np
from typing import Literal
import matplotlib.pyplot as plt

from Algo.path import Path
from Algo.sim import Grid
from Algo.utils import *
        
class Dubins:
    @staticmethod
    def rsr(start: tuple[float, float, float], goal: tuple[float, float, float], radius: int, **kwargs) -> tuple[float, list[Path]]:
        """
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param pivot1: (y,x) of first pivot point (start position)
        :param pivot2: (y,x) of second pivot point (goal position)
        :param radius: Minimum turning radius of the car
        :return total_len: total length of dubins path
        :return [Path1, Path2, Path3]: list of Path objects making up the dubins path, either 0 or 3 Path
        """
        pivot1, pivot2 = get_pivot(start, radius, "R"), get_pivot(goal, radius, "R")
        p1x, p1y = pivot1[1], pivot1[0]
        p2x, p2y = pivot2[1], pivot2[0]
        v1x, v1y = p2x-p1x, p2y-p1y
        v2x, v2y = -v1y, v1x
        len_v2 = np.linalg.norm([v2x, v2y])
        if len_v2 == 0: v2x, v2y = 0, 0
        else: v2x, v2y = v2x/len_v2, v2y/len_v2
        pt1x, pt1y = p1x + radius*v2x, p1y + radius*v2y
        pt2x, pt2y = pt1x+v1x, pt1y+v1y

        #find angle between start pivot1 and pt1
        angle1 = A((start[0],start[1]), (pt1y, pt1x), pivot1)
        if angle1 > 0:
            angle1  = angle1 - 2*np.pi
        len1 = np.abs(angle1)*radius

        #find angle between pt2 pivot2 and goal
        angle2 = A((pt2y, pt2x), (goal[0],goal[1]), pivot2)
        if angle2 > 0:
            angle2  = angle2 - 2*np.pi
        len2 = np.abs(angle2)*radius

        total_len = len1 + np.sqrt(v1x**2+v1y**2) + len2
        return (total_len, [Path(start=start, goal=(pt1y, pt1x, start[2]+angle1), steering="R", angle=abs(M(angle1)), radius=radius, **kwargs), 
                            Path(start=(pt1y,pt1x, start[2]+angle1), goal=(pt2y,pt2x, start[2]+angle1), **kwargs), 
                            Path(start=(pt2y, pt2x, start[2]+angle1), goal=goal, steering="R", angle=abs(M(angle2)), radius=radius, **kwargs)])

    @staticmethod
    def lsl(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param pivot1: (y,x) of first pivot point (start position)
        :param pivot2: (y,x) of second pivot point (goal position)
        :param radius: Minimum turning radius of the car
        :return total_len: total length of dubins path
        :return [Path1, Path2, Path3]: list of Path objects making up the dubins path, either 0 or 3 Path
        '''
        pivot1, pivot2 = get_pivot(start, radius, "L"), get_pivot(goal, radius, "L")
        p1x, p1y = pivot1[1], pivot1[0]
        p2x, p2y = pivot2[1], pivot2[0]
        v1x, v1y = p2x-p1x, p2y-p1y
        v2x, v2y = v1y, -v1x
        len_v2 = np.linalg.norm([v2x, v2y])
        if len_v2 == 0: v2x, v2y = 0, 0
        else: v2x, v2y = v2x/np.linalg.norm([v2x, v2y]), v2y/np.linalg.norm([v2x, v2y])
        pt1x, pt1y = p1x + radius*v2x, p1y + radius*v2y
        pt2x, pt2y = pt1x+v1x, pt1y+v1y

        #find angle between start pivot1 and pt1
        angle1 = A((start[0],start[1]), (pt1y, pt1x), pivot1)
        if angle1 < 0:
            angle1  = angle1 + 2*np.pi
        len1 = np.abs(angle1)*radius

        #find angle between pt2 pivot2 and goal
        angle2 = A((pt2y, pt2x), (goal[0],goal[1]), pivot2)
        if angle2 < 0:
            angle2  = angle2 + 2*np.pi
        len2 = np.abs(angle2)*radius

        total_len = len1 + np.sqrt(v1x**2+v1y**2) + len2
        return (total_len, [Path(start=start, goal=(pt1y, pt1x, start[2]+angle1), steering="L", angle=abs(M(angle1)), radius=radius, **kwargs), 
                            Path(start=(pt1y,pt1x, start[2]+angle1), goal=(pt2y,pt2x, start[2]+angle1), **kwargs), 
                            Path(start=(pt2y, pt2x, start[2]+angle1), goal=goal, steering="L", angle=abs(M(angle2)), radius=radius, **kwargs)])

    @staticmethod
    def rsl(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param pivot1: (y,x) of first pivot point (start position)
        :param pivot2: (y,x) of second pivot point (goal position)
        :param radius: Minimum turning radius of the car
        :return total_len: total length of dubins path
        :return [Path1, Path2, Path3]: list of Path objects making up the dubins path, either 0 or 3 Path
        '''
        pivot1, pivot2 = get_pivot(start, radius, "R"), get_pivot(goal, radius, "L")
        p1x, p1y = pivot1[1], pivot1[0]
        p2x, p2y = pivot2[1], pivot2[0]
        v1x, v1y = p2x-p1x, p2y-p1y
        d = np.sqrt(v1x**2+v1y**2)
        if(d < 2*radius):
            return (float('inf'), [])
        theta = np.arccos(2*radius/d)
        v2x, v2y = v1x*np.cos(theta)-v1y*np.sin(theta), v1x*np.sin(theta)+v1y*np.cos(theta)
        v2x, v2y = v2x/np.linalg.norm([v2x, v2y]), v2y/np.linalg.norm([v2x, v2y])
        pt1x, pt1y = p1x + radius*v2x, p1y + radius*v2y
        v3x, v3y = -v2x, -v2y
        pt2x, pt2y = p2x + radius*v3x, p2y + radius*v3y
        linex, liney = pt2x-pt1x, pt2y-pt1y

        #Right turn
        angle1 = A((start[0],start[1]), (pt1y, pt1x), pivot1)
        if angle1 > 0:
            angle1  = angle1 - 2*np.pi
        len1 = np.abs(angle1)*radius

        #find angle between pt2 pivot2 and goal
        angle2 = A((pt2y, pt2x), (goal[0],goal[1]), pivot2)
        if angle2 < 0:
            angle2  = angle2 + 2*np.pi
        len2 = np.abs(angle2)*radius

        total_len = len1 + np.sqrt(linex**2+liney**2) + len2
        return (total_len, [Path(start=start, goal=(pt1y, pt1x, start[2]+angle1), steering="R", angle=abs(M(angle1)), radius=radius, **kwargs), 
                            Path(start=(pt1y, pt1x, start[2]+angle1), goal=(pt2y, pt2x, start[2]+angle1), **kwargs), 
                            Path(start=(pt2y, pt2x, start[2]+angle1), goal=goal, steering="L", angle=abs(M(angle2)), radius=radius, **kwargs)])

    @staticmethod
    def lsr(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param pivot1: (y,x) of first pivot point (start position)
        :param pivot2: (y,x) of second pivot point (goal position)
        :param radius: Minimum turning radius of the car
        :return total_len: total length of dubins path
        :return [Path1, Path2, Path3]: list of Path objects making up the dubins path, either 0 or 3 Path
        '''
        pivot1, pivot2 = get_pivot(start, radius, "L"), get_pivot(goal, radius, "R")
        p1x, p1y = pivot1[1], pivot1[0]
        p2x, p2y = pivot2[1], pivot2[0]
        v1x, v1y = p2x-p1x, p2y-p1y
        d = np.sqrt(v1x**2+v1y**2)
        if(d < 2*radius):
            return (float('inf'), [])
        theta = np.arccos(2*radius/d)
        v2x, v2y = v1x*np.cos(-theta)-v1y*np.sin(-theta), v1x*np.sin(-theta)+v1y*np.cos(-theta)
        v2x, v2y = v2x/np.linalg.norm([v2x, v2y]), v2y/np.linalg.norm([v2x, v2y])
        pt1x, pt1y = p1x + radius*v2x, p1y + radius*v2y
        v3x, v3y = -v2x, -v2y
        pt2x, pt2y = p2x + radius*v3x, p2y + radius*v3y
        linex, liney = pt2x-pt1x, pt2y-pt1y

        #left turn
        angle1 = A((start[0],start[1]), (pt1y, pt1x), pivot1)
        if angle1 < 0:
            angle1  = angle1 + 2*np.pi
        len1 = np.abs(angle1)*radius

        #right turn
        angle2 = A((pt2y, pt2x), (goal[0], goal[1]), pivot2)
        if angle2 > 0:
            angle2  = angle2 - 2*np.pi
        len2 = np.abs(angle2)*radius

        total_len = len1 + np.sqrt(linex**2+liney**2) + len2
        return (total_len, [Path(start=start, goal=(pt1y, pt1x, start[2]+angle1), steering="L", angle=abs(M(angle1)), radius=radius, **kwargs), 
                            Path(start=(pt1y, pt1x, start[2]+angle1), goal=(pt2y, pt2x, start[2]+angle1), **kwargs), 
                            Path(start=(pt2y, pt2x, start[2]+angle1), goal=goal, steering="R", angle=abs(M(angle2)), radius=radius,**kwargs)])

    @staticmethod
    def rlr(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param pivot1: (y,x) of first pivot point (start position)
        :param pivot2: (y,x) of second pivot point (goal position)
        :param radius: Minimum turning radius of the car
        :return total_len: total length of dubins path
        :return [Path1, Path2, Path3]: list of Path objects making up the dubins path, either 0 or 3 Path
        '''
        pivot1, pivot2 = get_pivot(start, radius, "R"), get_pivot(goal, radius, "R")
        p1x, p1y = pivot1[1], pivot1[0]
        p2x, p2y = pivot2[1], pivot2[0]
        d = np.sqrt((p2x-p1x)**2+(p2y-p1y)**2)
        if d > 4*radius:
            return (float('inf'), [])
        qx, qy = (p1x+p2x)/2, (p1y+p2y)/2
        v1x, v1y = p2x-p1x, p2y-p1y
        v2x, v2y = p1y-p2y, p2x-p1x
        d1 = np.sqrt((2*radius)**2-(d/2)**2)
        len_v2 = np.linalg.norm([v2x, v2y])
        if len_v2 == 0: p3x, p3y = qx, qy
        else: p3x, p3y = qx + d1*v2x/np.linalg.norm([v2x, v2y]), qy + d1*v2y/np.linalg.norm([v2x, v2y])
        pt1x, pt1y = (p1x+p3x)/2, (p1y+p3y)/2
        pt2x, pt2y = (p2x+p3x)/2, (p2y+p3y)/2

        Angle1 = A((start[0],start[1]), (pt1y, pt1x), pivot1)
        if Angle1 > 0:
            Angle1  = Angle1 - 2*np.pi
        len1 = np.abs(Angle1)*radius

        Angle2 = A((pt1y, pt1x), (pt2y, pt2x), (p3y, p3x))
        if Angle2 < 0:
            Angle2  = Angle2 + 2*np.pi
        len2 = np.abs(Angle2)*radius

        Angle3 = A((pt2y, pt2x), (goal[0],goal[1]), pivot2)
        if Angle3 > 0:
            Angle3  = Angle3 - 2*np.pi
        len3 = np.abs(Angle3)*radius

        total_len = len1 + len2 + len3
        return (total_len, [Path(start=start, goal=(pt1y, pt1x, start[2]+Angle1), steering="R", angle=Angle1, radius=radius, **kwargs), 
                            Path(start=(pt1y, pt1x, start[2]+Angle1), goal=(pt2y, pt2x, start[2]+Angle1+Angle2), steering="L", angle=Angle2, radius=radius, **kwargs), 
                            Path(start=(pt2y, pt2x, start[2]+Angle1+Angle2), goal=goal, steering="R", angle=Angle3, radius=radius, **kwargs)])

    @staticmethod
    def lrl(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param pivot1: (y,x) of first pivot point (start position)
        :param pivot2: (y,x) of second pivot point (goal position)
        :param radius: Minimum turning radius of the car
        :return total_len: total length of dubins path
        :return [Path1, Path2, Path3]: list of Path objects making up the dubins path, either 0 or 3 Path
        '''
        pivot1, pivot2 = get_pivot(start, radius, "L"), get_pivot(goal, radius, "L")
        p1x, p1y = pivot1[1], pivot1[0]
        p2x, p2y = pivot2[1], pivot2[0]
        d = np.sqrt((p2x-p1x)**2+(p2y-p1y)**2)
        if d > 4*radius:
            return (float('inf'), [])
        qx, qy = (p1x+p2x)/2, (p1y+p2y)/2
        v1x, v1y = p2x-p1x, p2y-p1y
        v2x, v2y = p1y-p2y, p2x-p1x
        d1 = np.sqrt((2*radius)**2-(d/2)**2)
        len_v2 = np.linalg.norm([v2x, v2y])
        if len_v2 == 0: p3x, p3y = qx, qy
        else: p3x, p3y = qx + d1*v2x/np.linalg.norm([v2x, v2y]), qy + d1*v2y/np.linalg.norm([v2x, v2y])
        pt1x, pt1y = (p1x+p3x)/2, (p1y+p3y)/2
        pt2x, pt2y = (p2x+p3x)/2, (p2y+p3y)/2

        Angle1 = A((start[0],start[1]), (pt1y, pt1x), pivot1)
        if Angle1 < 0:
            Angle1  = Angle1 + 2*np.pi
        len1 = np.abs(Angle1)*radius

        Angle2 = A((pt1y, pt1x), (pt2y, pt2x), (p3y, p3x))
        if Angle2 > 0:
            Angle2  = Angle2 - 2*np.pi
        len2 = np.abs(Angle2)*radius

        Angle3 = A((pt2y, pt2x), (goal[0],goal[1]), pivot2)
        if Angle3 < 0:
            Angle3  = Angle3 + 2*np.pi
        len3 = np.abs(Angle3)*radius

        total_len = len1 + len2 + len3
        return (total_len, [Path(start=start, goal=(pt1y, pt1x, start[2]+Angle1), steering="L", angle=Angle1, radius=radius, **kwargs), 
                            Path(start=(pt1y, pt1x, start[2]+Angle1), goal=(pt2y, pt2x, start[2]+Angle1+Angle2), steering="R", angle=Angle2, radius=radius, **kwargs), 
                            Path(start=(pt2y, pt2x, start[2]+Angle1+Angle2), goal=goal, steering="L", angle=Angle3, radius=radius, **kwargs)])

    @staticmethod
    def compute_all_path(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param radius: Minimum turning radius of the car
        :return all_path: list of all possible dubins path
        '''
        all_path = [
            Dubins.rsr(start, goal, radius, **kwargs),
            Dubins.lsl(start, goal, radius, **kwargs),
            Dubins.rsl(start, goal, radius, **kwargs),
            Dubins.lsr(start, goal, radius, **kwargs),
            Dubins.rlr(start, goal, radius, **kwargs),
            Dubins.lrl(start, goal, radius, **kwargs)
        ]
        all_path.sort(key=lambda x: x[0])
        return all_path
    @staticmethod
    def compute_shortest_path(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param radius: Minimum turning radius of the car
        :return total_len: total length of shortest dubins path'''
        all_path = Dubins.compute_all_path(start, goal, radius, **kwargs)
        return all_path[0]
    
    @staticmethod
    def compute_shortest_valid_path(start, goal, turning_radius, env: Grid, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param radius: Minimum turning radius of the car
        :param env: Grid object representing the environment
        :return total_len: total length of shortest dubins path
        '''
        all_path = Dubins.compute_all_path(start, goal, turning_radius, **kwargs)
        for total, path in all_path:
            if(total == float('inf')):
                continue
            valid = True
            for seg in path:
                seg.generate_path(**kwargs)
                if not env.isvalidpath(seg):
                    valid = False
                    break
        
            if valid:
                return (total, path, path[-1].goal)
        return (float("inf"), [], None)
    
    @staticmethod
    def compute_shortest_isvalid_path(start, goal, radius, env: Grid, **kwargs):
        '''
        :param start: (y,x,theta) of start position
        :param goal: (y,x,theta) of goal position
        :param radius: Minimum turning radius of the car
        :param env: Grid object representing the environment
        :return total_len: total length of shortest dubins path
        '''
        path = Dubins.compute_shortest_path(start, goal, radius, **kwargs)
        for seg in path[1]:
            seg.generate_path(**kwargs)
            if not env.isvalidpath(seg):
                return (float("inf"), [], None)
    
        return (path[0], path[1], path[1].goal)


