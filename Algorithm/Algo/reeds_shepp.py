from Algo.utils import *
from Algo.path import Path
from dataclasses import dataclass, replace
from enum import Enum
import math

class Steering(Enum):
    LEFT = -1
    RIGHT = 1
    STRAIGHT = 0

class Gear(Enum):
    FORWARD = 1
    BACKWARD = -1

@dataclass(eq=True)
class PathElement:
    param: float
    steering: Steering
    gear: Gear

    @classmethod
    def create(cls, param: float, steering: Steering, gear: Gear):
        if param >= 0:
            return cls(param, steering, gear)
        else:
            return cls(-param, steering, gear).reverse_gear()

    def __repr__(self):
        s = "{ Steering: " + self.steering.name + "\tGear: " + self.gear.name \
            + "\tdistance: " + str(round(self.param, 2)) + " }"
        return s

    def reverse_steering(self):
        steering = Steering(-self.steering.value)
        return replace(self, steering=steering)

    def reverse_gear(self):
        gear = Gear(-self.gear.value)
        return replace(self, gear=gear)

def timeflip(path):
    """
    timeflip transform described around the end of the article
    """
    new_path = [e.reverse_gear() for e in path]
    return new_path


def reflect(path):
    """
    reflect transform described around the end of the article
    """
    new_path = [e.reverse_steering() for e in path]
    return new_path

class ReedsShepp:
    """
    Mostly from https://github.com/nathanlct/reeds-shepp-curves/blob/master/ReedsShepp.py
    """
    @staticmethod
    def timeflip(path):
        '''
        :param path: list of Path segments
        :return: list of Path segments
        '''
        new_path = [p.timeflip() for p in path]
        return new_path

    @staticmethod
    def reflect(path):
        '''
        :param path: list of Path segments
        :return: list of Path segments
        '''
        new_path = [p.reflect() for p in path]
        return new_path

    @staticmethod
    def path1(start, x, y, phi, radius=2):
        """
        Formula 8.1: CSC (same turns)
        """
        path = []

        u, t = R(x - np.sin(phi), y - 1 + np.cos(phi))
        v = M(phi - t)

        path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
        path.append(PathElement.create(u, Steering.STRAIGHT, Gear.FORWARD))
        path.append(PathElement.create(v, Steering.LEFT, Gear.FORWARD))

        return path

    @staticmethod
    def path2(start, x, y, phi, radius=2):
        """
        Formula 8.2: CSC (opposite turns)
        """
        phi = M(phi)
        path = []

        rho, t1 = R(x + np.sin(phi), y - 1 - np.cos(phi))

        if rho * rho >= 4:
            u = np.sqrt(rho * rho - 4)
            t = M(t1 + np.atan2(2, u))
            v = M(t - phi)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.STRAIGHT, Gear.FORWARD))
            path.append(PathElement.create(v, Steering.RIGHT, Gear.FORWARD))

        return path

    @staticmethod
    def path3(start, x, y, phi):
        """
        Formula 8.3: C|C|C
        """
        path = []

        xi = x - np.sin(phi)
        eta = y - 1 + np.cos(phi)
        rho, theta = R(xi, eta)

        if rho <= 4:
            A = np.acos(rho / 4)
            t = M(theta + np.pi/2 + A)
            u = M(np.pi - 2*A)
            v = M(phi - t - u)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.RIGHT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.LEFT, Gear.FORWARD))

        return path

    @staticmethod
    def path4(start, x, y, phi):
        """
        Formula 8.4 (1): C|CC
        """
        path = []

        xi = x - np.sin(phi)
        eta = y - 1 + np.cos(phi)
        rho, theta = R(xi, eta)

        if rho <= 4:
            A = np.acos(rho / 4)
            t = M(theta + np.pi/2 + A)
            u = M(np.pi - 2*A)
            v = M(t + u - phi)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.RIGHT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.LEFT, Gear.BACKWARD))

        return path

    @staticmethod
    def path5(start, x, y, phi):
        """
        Formula 8.4 (2): CC|C
        """

        path = []

        xi = x - np.sin(phi)
        eta = y - 1 + np.cos(phi)
        rho, theta = R(xi, eta)

        if rho <= 4:
            u = np.acos(1 - rho*rho/8)
            if rho==0: return path
            A = np.asin(2 * np.sin(u) / rho)   
            t = M(theta + np.pi/2 - A)
            v = M(t - u - phi)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.RIGHT, Gear.FORWARD))
            path.append(PathElement.create(v, Steering.LEFT, Gear.BACKWARD))

        return path

    @staticmethod
    def path6(start, x, y, phi):
        """
        Formula 8.7: CCu|CuC
        """
        path = []

        xi = x + np.sin(phi)
        eta = y - 1 - np.cos(phi)
        rho, theta = R(xi, eta)

        if rho <= 4:
            if rho <= 2:
                A = np.acos((rho + 2) / 4)
                t = M(theta + np.pi/2 + A)
                u = M(A)
                v = M(phi - t + 2*u)
            else:
                A = np.acos((rho - 2) / 4)
                t = M(theta + np.pi/2 - A)
                u = M(np.pi - A)
                v = M(phi - t + 2*u)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.RIGHT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.LEFT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.RIGHT, Gear.BACKWARD))

        return path
    
    @staticmethod
    def path7(start, x, y, phi):
        """
        Formula 8.8: C|CuCu|C
        """
        path = []

        xi = x + np.sin(phi)
        eta = y - 1 - np.cos(phi)
        rho, theta = R(xi, eta)
        u1 = (20 - rho*rho) / 16

        if rho <= 6 and 0 <= u1 <= 1:
            u = np.acos(u1)
            A = np.asin(2 * np.sin(u) / rho)
            t = M(theta + np.pi/2 + A)
            v = M(t - phi)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.RIGHT, Gear.BACKWARD))
            path.append(PathElement.create(u, Steering.LEFT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.RIGHT, Gear.FORWARD))

        return path

    def path8(start, x, y, phi):
        """
        Formula 8.9 (1): C|C[pi/2]SC
        """
        path = []

        xi = x - np.sin(phi)
        eta = y - 1 + np.cos(phi)
        rho, theta = R(xi, eta)

        if rho >= 2:
            u = np.sqrt(rho*rho - 4) - 2
            A = np.atan2(2, u+2)
            t = M(theta + np.pi/2 + A)
            v = M(t - phi + np.pi/2)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(np.pi/2, Steering.RIGHT, Gear.BACKWARD))
            path.append(PathElement.create(u, Steering.STRAIGHT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.LEFT, Gear.BACKWARD))

        return path
    
    @staticmethod
    def path9(start, x, y, phi):
        """
        Formula 8.9 (2): CSC[pi/2]|C
        """
        path = []

        xi = x - np.sin(phi)
        eta = y - 1 + np.cos(phi)
        rho, theta = R(xi, eta)

        if rho >= 2:
            u = np.sqrt(rho*rho - 4) - 2
            A = np.atan2(u+2, 2)
            t = M(theta + np.pi/2 - A)
            v = M(t - phi - np.pi/2)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.STRAIGHT, Gear.FORWARD))
            path.append(PathElement.create(np.pi/2, Steering.RIGHT, Gear.FORWARD))
            path.append(PathElement.create(v, Steering.LEFT, Gear.BACKWARD))

        return path

    @staticmethod
    def path10(start, x, y, phi):
        """
        Formula 8.10 (1): C|C[pi/2]SC
        """
        path = []

        xi = x + np.sin(phi)
        eta = y - 1 - np.cos(phi)
        rho, theta = R(xi, eta)

        if rho >= 2:
            t = M(theta + np.pi/2)
            u = rho - 2
            v = M(phi - t - np.pi/2)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(np.pi/2, Steering.RIGHT, Gear.BACKWARD))
            path.append(PathElement.create(u, Steering.STRAIGHT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.RIGHT, Gear.BACKWARD))

        return path
    
    @staticmethod
    def path11(start, x, y, phi):
        """
        Formula 8.10 (2): CSC[pi/2]|C
        """
        path = []

        xi = x + np.sin(phi)
        eta = y - 1 - np.cos(phi)
        rho, theta = R(xi, eta)

        if rho >= 2:
            t = M(theta)
            u = rho - 2
            v = M(phi - t - np.pi/2)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(u, Steering.STRAIGHT, Gear.FORWARD))
            path.append(PathElement.create(np.pi/2, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(v, Steering.RIGHT, Gear.BACKWARD))

        return path
    
    @staticmethod
    def path12(start, x, y, phi):
        """
        Formula 8.11: C|C[pi/2]SC[pi/2]|C
        """
        path = []

        xi = x + np.sin(phi)
        eta = y - 1 - np.cos(phi)
        rho, theta = R(xi, eta)

        if rho >= 4:
            u = np.sqrt(rho*rho - 4) - 4
            A = np.atan2(2, u+4)
            t = M(theta + np.pi/2 + A)
            v = M(t - phi)

            path.append(PathElement.create(t, Steering.LEFT, Gear.FORWARD))
            path.append(PathElement.create(np.pi/2, Steering.RIGHT, Gear.BACKWARD))
            path.append(PathElement.create(u, Steering.STRAIGHT, Gear.BACKWARD))
            path.append(PathElement.create(np.pi/2, Steering.LEFT, Gear.BACKWARD))
            path.append(PathElement.create(v, Steering.RIGHT, Gear.FORWARD))

        return path

    @staticmethod
    def compute_all_paths(start, goal, turning_radius=2, **kwargs):
        '''
        :param start: (y,x,theta) tuple
        :param goal: (y,x,theta) tuple
        :param turning_radius: float
        :return: list of Path segments
        '''
        path_fns = [ReedsShepp.path1, ReedsShepp.path2, ReedsShepp.path3, ReedsShepp.path4, ReedsShepp.path5, ReedsShepp.path6,
                    ReedsShepp.path7, ReedsShepp.path8, ReedsShepp.path9, ReedsShepp.path10, ReedsShepp.path11, ReedsShepp.path12]
        paths = []

        # get coordinates of end in the set of axis where start is (0,0,0)
        tmpstart = (start[1]/turning_radius, start[0]/turning_radius, start[2]) #Swap x,y for calculation
        tmpgoal = (goal[1]/turning_radius, goal[0]/turning_radius, goal[2])
        x, y, theta = change_of_basis(tmpstart, tmpgoal)

        for get_path in path_fns:
            # get the four variants for each path type, cf article
            paths.append(get_path(start, x, y, theta))
            paths.append(timeflip(get_path(start, -x, y, -theta)))
            paths.append(reflect(get_path(start, x, -y, -theta)))
            paths.append(reflect(timeflip(get_path(start, -x, -y, theta))))

        #remove path elements that have parameter 0
        for i in range(len(paths)):
            paths[i] = list(filter(lambda e: e.param != 0, paths[i]))

        # remove empty paths
        paths = list(filter(None, paths))

        ret = []
        for path in paths:
            tmp = []
            for i in range(len(path)):
                if i == 0:
                    if path[i].steering == Steering.LEFT:
                        tmp.append(Path(start=start, angle=round(path[i].param/np.pi *180)/180 * np.pi, steering="L", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                    elif path[i].steering == Steering.RIGHT:
                        tmp.append(Path(start=start, angle=round(path[i].param/np.pi *180)/180 * np.pi, steering="R", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                    else:
                        tmp.append(Path(start=start, len=round(path[i].param*turning_radius), forward=path[i].gear == Gear.FORWARD))
                else:
                    if path[i].steering == Steering.LEFT:
                        tmp.append(Path(start=tmp[-1].goal, angle=round(path[i].param/np.pi *180)/180 * np.pi, steering="L", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                    elif path[i].steering == Steering.RIGHT:
                        tmp.append(Path(start=tmp[-1].goal, angle=round(path[i].param/np.pi *180)/180 * np.pi, steering="R", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                    else:
                        tmp.append(Path(start=tmp[-1].goal, len=round(path[i].param*turning_radius), forward=path[i].gear == Gear.FORWARD))
                
                # optimistic algorithm
                # if i == 0:
                #     if path[i].steering == Steering.LEFT:
                #         tmp.append(Path(start=start, angle=path[i].param, steering="L", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                #     elif path[i].steering == Steering.RIGHT:
                #         tmp.append(Path(start=start, angle=path[i].param, steering="R", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                #     else:
                #         tmp.append(Path(start=start, len=path[i].param*turning_radius, forward=path[i].gear == Gear.FORWARD))
                # else:
                #     if path[i].steering == Steering.LEFT:
                #         tmp.append(Path(start=tmp[-1].goal, angle=path[i].param, steering="L", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                #     elif path[i].steering == Steering.RIGHT:
                #         tmp.append(Path(start=tmp[-1].goal, angle=path[i].param, steering="R", forward=path[i].gear == Gear.FORWARD, radius=turning_radius))
                #     else:
                #         tmp.append(Path(start=tmp[-1].goal, len=path[i].param*turning_radius, forward=path[i].gear == Gear.FORWARD))
            ret.append(tmp)

        for i in range(len(ret)):
            total_len = 0
            for seg in ret[i]:
                if seg.straight: total_len += seg.len
                else: total_len += seg.angle*turning_radius + turning_radius/2
            ret[i] = (total_len, ret[i], ret[i][-1].goal)
        return ret

    @staticmethod
    def compute_shortest_path(start, goal, radius, **kwargs):
        '''
        :param start: (y,x,theta) tuple
        :param goal: (y,x,theta) tuple
        :param turning_radius: float
        :return total: total distance of the path
        :return path: list of Path segments
        :return goal_loc: (y,x,theta) tuple, the final position
        '''
        all_paths = ReedsShepp.compute_all_paths(
            start, goal, radius, **kwargs)
        all_paths = sorted(all_paths, key=lambda x: x[0])
        return all_paths[0]

    @staticmethod
    def compute_shortest_valid_path(start, goal, radius, env, **kwargs):
        '''
        :param start: (y,x,theta) tuple
        :param goal: (y,x,theta) tuple
        :param turning_radius: float
        :param env: Grid object
        :return total: total distance of the path
        :return path: list of Path segments
        :return goal_loc: (y,x,theta) tuple, the final position
        '''
        all_path = ReedsShepp.compute_all_paths(start, goal, radius, **kwargs)
        all_path = sorted(all_path, key=lambda x: x[0])
        for total, path, goal in all_path:
            valid = True
            for seg in path:
                seg.generate_path(**kwargs)
                if not env.isvalidpath(seg):
                    valid = False
                    break
            if valid:
                return (total, path, goal)
        return (float("inf"), [], None)
    
    @staticmethod
    def compute_shortest_isvalid_path(start, goal, radius, env, **kwargs):
        shortest = ReedsShepp.compute_shortest_path(start, goal, radius, **kwargs)
        for seg in shortest[1]:
            seg.generate_path(**kwargs)
            if not env.isvalidpath(seg):
                return (float("inf"), [], None)
        return shortest