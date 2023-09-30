from dataclasses import dataclass
from enum import Enum
import random
import string
from pygame import Color
from constants import *


@dataclass
class Point:
    x: int
    y: int


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

dir_axis = {Direction.RIGHT: (1, 0),
            Direction.LEFT: (-1, 0),
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1)
            }

class Road:
    def __init__(self,
                 name: str,
                 horizontal: bool,
                 top: int,
                 left: int,
                 right: int) -> None:
        self.name = name
        self.horizontal = horizontal
        self.top = top
        self.left = left
        self.right = right

        self.left_lanes = [Lane(self, i, Direction.LEFT if self.horizontal else Direction.UP, 
                                 self.top + i * BLOCK_SIZE + i * LANE_DISPLACEMENT)
                           for i in range(self.left)]
        
        self.right_lanes = [Lane(self, i, Direction.RIGHT if self.horizontal else Direction.DOWN, 
                                 self.top + i * BLOCK_SIZE + i * LANE_DISPLACEMENT + 
                                 self.left * BLOCK_SIZE + self.left * LANE_DISPLACEMENT)
                           for i in range(self.right)]
        
        self.half = self.top + self.left * BLOCK_SIZE + (self.left - 1) * LANE_DISPLACEMENT
        self.bottom = self.top + (self.left + self.right) * BLOCK_SIZE + (self.left + self.right - 1) * LANE_DISPLACEMENT
        

class Lane:
    def __init__(self,
                 road: Road,
                 num: int,
                 dir: Direction,
                 top: int) -> None:
        self.road = road
        self.num = num
        self.top = top
        self.dir = dir


class Car:
    def __init__(self,
                 name: str,
                 loc:int,
                 road:Road,
                 lane:int,
                 dir:Direction,
                 speed:int,
                 size:int,
                 accelaration:int,
                 color: Color) -> None:
        
        assert (0 <= lane <= road.left - 1 and (dir == Direction.LEFT or dir == Direction.UP)) or \
            (0 <= lane <= road.right - 1 and (dir == Direction.RIGHT or dir == Direction.DOWN)), \
            f"The Lane {lane} given in Car {name} does not exists in road {road.id}"
        
        assert 0 <= loc <= WINDOW_SIZE, \
            f"Car {name}'s position is outside the window. WINDOW_SIZE = {WINDOW_SIZE}"
        
        self.name = name
        self.road = road
        self.dir = dir
        self.speed = speed
        self.size = size
        self.accelaration = accelaration
        self.color = color
        self.dead = False

        self.lanes = self.road.left_lanes if self.dir == Direction.LEFT or self.dir == Direction.UP \
                    else self.road.right_lanes

        self.lane = self.lanes[lane]
        
        self.pos = Point(loc, self.lane.top) if self.road.horizontal \
                    else Point(self.lane.top, loc)
        
        self.w = self.size if self.road.horizontal else BLOCK_SIZE
        self.h = BLOCK_SIZE if self.road.horizontal else self.size
        
    def move(self, x, y):
        self.pos.x += x
        self.pos.y += y
        
    def change_lane(self, lane_diff):
        if 0 <= self.lane.num + lane_diff < len(self.lanes) :
            self.lane = self.lanes[self.lane.num + lane_diff]
            self.update_position()
            return True
        return False
        
    def turn(self, roads, new_dir):
        self.dir = new_dir
        loc = self.pos.x if self.road.horizontal else self.pos.y
        
        for road in roads:
            if road.horizontal != self.road.horizontal:
                for lane in road.left_lanes:
                    if lane.top <= loc <= lane.top + BLOCK_SIZE:
                        self.road = road
                        self.lane = lane
                        self.update_position()
                        self.w, self.h = self.h, self.w
                        return True
                for lane in road.right_lanes:
                    if lane.top <= loc <= lane.top + BLOCK_SIZE:
                        self.road = road
                        self.lane = lane
                        self.update_position()
                        self.w, self.h = self.h, self.w
                        return True
        return False

    def update_position(self):
        if self.road.horizontal:
            self.pos.y = self.lane.top
        else:
            self.pos.x = self.lane.top
        if self.dir == Direction.LEFT or self.dir == Direction.UP:
            self.lanes = self.road.left_lanes
        else:
            self.lanes = self.road.right_lanes

    def __str__(self):
        return f"name {self.name}, lane {self.lane.num}, loc {self.loc}, pos ({self.pos.x}, {self.pos.y}), dir {self.dir}"


class Goal:
    def __init__(self, lane:Lane, loc: int, car:Car) -> None:
        self.lane = lane
        self.loc = loc
        self.car = car

        self.pos = Point(self.loc, self.lane.top) if self.lane.road.horizontal \
                   else Point(self.lane.top, self.loc)
        

def overlap(p1, w1, h1, p2, w2, h2):
    
    # If one rectangle is on left side of other
    if p1.x > p2.x + w2 or p2.x > p1.x + w1:
        return False
 
    # If one rectangle is above other
    if p1.y > p2.y + h2 or p2.y > p1.y + h1:
        return False
 
    return True


def create_random_car(roads:list[Road], cars) -> Car:
    road = random.choice(roads)
    lane = random.choice(road.left_lanes + road.right_lanes)

    loc = random.randint(BLOCK_SIZE, WINDOW_SIZE - BLOCK_SIZE)
    size = random.randint(BLOCK_SIZE // 2, BLOCK_SIZE * 2)
    p = Point(loc, lane.top) if road.horizontal \
        else Point(lane.top, loc)
    while any([overlap(p, 
                       size if road.horizontal else BLOCK_SIZE, 
                       BLOCK_SIZE if road.horizontal else size, 
                       cars[i].pos, cars[i].w, cars[i].h) 
                for i in range(len(cars))]):
        loc = random.randint(BLOCK_SIZE, WINDOW_SIZE -BLOCK_SIZE)
        p = Point(loc, lane.top) if lane.road.horizontal \
            else Point(lane.top, loc)
    
    speed = random.randint(BLOCK_SIZE // 2, BLOCK_SIZE * 2)
    accelaration = random.choice([-1, 0, 1])
    color = random.choice(COLORS)
    name = random.choice(string.ascii_uppercase)

    return Car(name=name, 
               loc=loc, 
               road=road, 
               lane=lane.num, 
               dir=lane.dir, 
               speed=speed, 
               accelaration=accelaration,
               size=size,
               color=color)
