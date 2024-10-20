import numpy as np
from enum import Enum
from typing import Literal
from Algo.utils import *

class Path:
    angle2 = None # Used for calculation where +ve is anti-clockwise and -ve is clockwise
    path_coords = None
    def __init__(self, start=None, goal=None, steering: Literal["L","R"] = None, angle=None, len=None, forward=True, radius=None, **kwargs):
        self.forward = forward
        self.radius = radius
        if angle is None: # Straight path
            self.straight = True
            if len is not None:
                if self.forward: goal = (start[0]+len*np.sin(start[2]), start[1]+len*np.cos(start[2]), start[2])
                else: goal = (start[0]-len*np.sin(start[2]), start[1]-len*np.cos(start[2]), start[2])
            elif goal is not None:
                len = np.sqrt((goal[0]-start[0])**2 + (goal[1]-start[1])**2)
        else: # Curve path
             # Should be only used for reeds shepp
            goal = self.generate_curve_goal(start, angle, steering, forward)
            # else: # Should be only used for Dubins
            #     self.pivot = get_pivot(start, radius, steering)
            self.straight = False
        self.steering = steering
        self.angle = angle
        self.start = start
        self.goal = goal
        self.len = len
        self.forward = forward
    
    def timeflip(self):
        if self.straight:
            return Path(self.start, len=self.len, forward=not self.forward)
        else:
            return Path(self.start, angle=self.angle, steering=self.steering, forward=not self.forward)
        
    def reflect(self):
        if self.straight:
            return Path(self.start, len=self.len, forward=self.forward)
        else:
            return Path(self.start, angle=self.angle, steering="L" if self.steering == "R" else "R", forward=self.forward)

    def generate_curve_goal(self, start, angle, steering, forward):
        if not forward:
            start = (start[0], start[1], M(start[2]+np.pi))
        start_y, start_x, start_theta = start
        if forward: 
            pivot_y, pivot_x = get_pivot(start, self.radius, steering)
            if steering=="R":
                if angle>0: angle = -angle
            else:
                if angle<0: angle = -angle
        else:
            if steering=="L": 
                pivot_y, pivot_x = get_pivot(start, self.radius, "R")
                if angle>0: angle = -angle
            else: 
                pivot_y, pivot_x = get_pivot(start, self.radius, "L")
    
        self.pivot = (pivot_y, pivot_x)
        v1x, v1y = start_x-pivot_x, start_y-pivot_y
        self.angle2 = angle
        final_angle = start_theta+angle
        if not forward: final_angle = M(final_angle+np.pi)
        return (v1y*np.cos(angle)+v1x*np.sin(angle)+pivot_y, v1x*np.cos(angle)-v1y*np.sin(angle)+pivot_x, final_angle)

        
    def generate_path(self, **kwargs):
        if self.straight:
            self.path_coords = self.generate_straight_path(**kwargs)
        else:
            self.path_coords = self.generate_curve_path(**kwargs)
        
    def generate_curve_path(self, **kwargs):
        start = self.start
        pivot = self.pivot
        if self.angle2!=None: angle = self.angle2
        else: angle = self.angle
        if not self.forward: 
            start = (start[0], start[1], M(start[2]+np.pi))
        path = []
        start_y, start_x, start_theta = start
        pivot_y, pivot_x = pivot
        v1x, v1y = start_x-pivot_x, start_y-pivot_y
        if angle > 0:
            for i in np.arange(0, angle, kwargs.get('curve_resolution', 0.1)):
                new_x = v1x*np.cos(i) - v1y*np.sin(i)
                new_y = v1x*np.sin(i) + v1y*np.cos(i)
                if not self.forward: path.append((new_y+pivot_y, new_x+pivot_x, M(start_theta+i+np.pi)))
                else: path.append((new_y+pivot_y, new_x+pivot_x, start_theta+i))
            if self.forward: self.goal = (v1x*np.sin(angle)+v1y*np.cos(angle)+pivot_y, v1x*np.cos(angle)-v1y*np.sin(angle)+pivot_x, start_theta+angle)
            else: self.goal = (v1x*np.sin(angle)+v1y*np.cos(angle)+pivot_y, v1x*np.cos(angle)-v1y*np.sin(angle)+pivot_x, M(start_theta+angle+np.pi))
            if self.goal[2] > np.pi:
                self.goal = (self.goal[0], self.goal[1], self.goal[2]-2*np.pi)
            elif self.goal[2] <= -np.pi:
                self.goal = (self.goal[0], self.goal[1], self.goal[2]+2*np.pi)
            path.append(self.goal)
        else:
            for i in np.arange(0, angle, -kwargs.get('curve_resolution', 0.1)):
                new_x = v1x*np.cos(i) - v1y*np.sin(i)
                new_y = v1x*np.sin(i) + v1y*np.cos(i)
                if not self.forward: path.append((new_y+pivot_y, new_x+pivot_x, M(start_theta+i+np.pi)))
                else: path.append((new_y+pivot_y, new_x+pivot_x, start_theta+i))
            if self.forward: self.goal = (v1x*np.sin(angle)+v1y*np.cos(angle)+pivot_y, v1x*np.cos(angle)-v1y*np.sin(angle)+pivot_x, start_theta+angle)
            else: self.goal = (v1x*np.sin(angle)+v1y*np.cos(angle)+pivot_y, v1x*np.cos(angle)-v1y*np.sin(angle)+pivot_x, M(start_theta+angle+np.pi))
            if self.goal[2] > np.pi:
                self.goal = (self.goal[0], self.goal[1], self.goal[2]-2*np.pi)
            elif self.goal[2] < -np.pi:
                self.goal = (self.goal[0], self.goal[1], self.goal[2]+2*np.pi)
            path.append(self.goal)        
        return path
    
    def generate_straight_path(self, **kwargs):
        start = self.start
        goal = self.goal
        if not self.forward:
            start = (start[0], start[1], M(start[2]+np.pi))
        path = []
        start_y, start_x, start_theta = start
        goal_y, goal_x, goal_theta = goal
        v1x, v1y = goal_x-start_x, goal_y-start_y
        for i in np.arange(0, np.sqrt(v1x**2+v1y**2), kwargs.get('line_resolution', 0.1)):
            new_x = v1x * i/np.sqrt(v1x**2+v1y**2)
            new_y = v1y * i/np.sqrt(v1x**2+v1y**2)
            if self.forward: path.append((new_y+start_y, new_x+start_x, start_theta))
            else: path.append((new_y+start_y, new_x+start_x, M(start_theta+np.pi)))
        path.append(goal)
        # else:
        #     for i in np.arange(0, -np.sqrt(v1x**2+v1y**2), kwargs.get('line_resolution', -0.1)):
        #         new_x = v1x * i/np.sqrt(v1x**2+v1y**2)
        #         new_y = v1y * i/np.sqrt(v1x**2+v1y**2)
        #         path.append((new_y+start_y, new_x+start_x, start_theta))
        #     path.append(goal)
        
        return path