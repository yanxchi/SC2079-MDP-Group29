import numpy as np
import matplotlib.pyplot as plt
from typing import Literal


def path_to_coord(paths):
    '''
    :param path: list of Paths
    :return: list of (y,x,theta) points representing the coordinates of the path
    '''
    coord = []
    for p in paths:
        for pseg in p:
            if pseg.path_coords == None:
                pseg.generate_path()
            coord += pseg.path_coords
    return coord


def A(point1, point2, pivot):
    '''
    Find the angle of rotation from point1 to point2 about pivot

    :param point1: (y,x) tuple
    :param point2: (y,x) tuple
    :param pivot: (y,x) tuple
    :return theta: angle of rotation in radians
    '''
    y1, x1 = point1[0], point1[1]
    y2, x2 = point2[0], point2[1]
    py, px = pivot[0], pivot[1]
    v1x, v1y = x1-px, y1-py
    v2x, v2y = x2-px, y2-py
    alpha = np.arctan2(v2y, v2x) - np.arctan2(v1y, v1x)
    return alpha

def M(theta):
    """
    Return the angle phi = theta mod (2 pi) such that -pi <= theta < pi.
    """
    theta = theta % (2*np.pi)
    if theta < -np.pi: return theta + 2 * np.pi
    if theta >= np.pi: return theta - 2 * np.pi
    return theta

def R(x, y):
    """
    Return the polar coordinates (r, theta) of the point (x, y).
    """
    
    r = np.sqrt(x*x + y*y)
    theta = np.atan2(y, x)
    return r, theta

def change_of_basis(p1, p2):
    """
    Given p1 = (x1, y1, theta1) and p2 = (x2, y2, theta2) represented in a
    coordinate system with origin (0, 0) and rotation 0 (in degrees), return
    the position and rotation of p2 in the coordinate system which origin
    (x1, y1) and rotation theta1.
    """
    theta1 = p1[2]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    new_x = dx * np.cos(theta1) + dy * np.sin(theta1)
    new_y = -dx * np.sin(theta1) + dy * np.cos(theta1)
    new_theta = p2[2] - p1[2]
    return new_x, new_y, new_theta

def get_pivot(pos, radius, side: Literal["L", "R"]):
    '''
    Find the pivot point for the car

    :param pos: (y,x,theta) tuple
    :param radius: radius of the car
    :param side: "L" or "R" for left or right turn
    :return pivot: (y,x) tuple
    '''
    v1y, v1x = np.sin(pos[2]), np.cos(pos[2])
    v1y, v1x = v1y/np.linalg.norm([v1y, v1x]), v1x/np.linalg.norm([v1y, v1x])
    if side == "R":
        v1x, v1y = v1y, -v1x
    elif side == "L":
        v1x, v1y = -v1y, v1x

    return (pos[0]+radius*v1y, pos[1]+radius*v1x)


def get_stopping_pos(target, distance=4) -> list[tuple]:
    '''
    Find the possible stopping positions for the car

    :param target: Target object
    :param distance: distance from the target
    :return coordinates: list of (y,x,theta) tuples for stopping positions
    '''
    if target.direction == "N":
        return [(target.y+distance, target.x-1, -np.pi/2), (target.y+distance, target.x, -np.pi/2), (target.y+distance, target.x+1, -np.pi/2)]
    elif target.direction == "S":
        return [(target.y-distance, target.x-1, np.pi/2), (target.y-distance, target.x, np.pi/2), (target.y-distance, target.x+1, np.pi/2)]
    elif target.direction == "W":
        return [(target.y-1, target.x-distance, 0), (target.y, target.x-distance, 0), (target.y+1, target.x-distance, 0)]
    elif target.direction == "E":
        return [(target.y-1, target.x+distance, np.pi), (target.y, target.x+distance, np.pi), (target.y+1, target.x+distance, np.pi)]


def plot_path(obstacles=[], path=None, start=None, goal=None):
    '''
    :param obstacles: list of Obstacle/Target objects
    :param path: list of (y,x,theta) points representing the path
    :param start: (y,x,theta) of start position
    :param goal: (y,x,theta) of goal position
    '''
    fig, ax = plt.subplots()

    # Plot the obstacles
    for obs in obstacles:
        oy, ox, orad = obs.get_pos()
        circle = plt.Circle((ox, oy), 0.5, color='red',
                            fill=True, alpha=0.5)
        ax.add_patch(circle)

    # Plot the Dubins path
    if path is not None:
        path = np.array(path)
        plt.plot(path[:, 1], path[:, 0], 'b-', markersize=1, label="Path")
    # Plot start and goal points
    if start is not None:
        plt.plot(start[1], start[0], "go", label="Start", markersize=10)
    if goal is not None:
        plt.plot(goal[1], goal[0], "ro", label="Goal", markersize=10)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_xticks(np.arange(0, 21, 1))
    ax.set_yticks(np.arange(0, 21, 1))
    ax.set_aspect('equal')
    plt.legend()
    plt.grid(True)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Path Planning with Obstacles")
    plt.show()

def round_angle(angle):
    '''
    :param angle: angle in radians
    :return: angle rounded to the nearest multiple of 45 degrees
    '''
    return round(angle/(np.pi/4)) * np.pi/4