from dataclasses import dataclass
from enum import Enum
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


class Problem(Enum):
    NO_NEXT_SEGMENT = 1
    CHANGE_LANE_WHILE_CROSSING = 2
    SLOWER_WHILE_0 = 3
    FASTER_WHILE_MAX = 4
    NO_ADJACENT_LANE = 5


direction_axis = {Direction.RIGHT: (1, 0),
                  Direction.LEFT: (-1, 0),
                  Direction.UP: (0, 1),
                  Direction.DOWN: (0, -1)
                  }

true_direction = {Direction.RIGHT: True,
                  Direction.LEFT: False,
                  Direction.UP: True,
                  Direction.DOWN: False
                  }

horiz_direction = {Direction.RIGHT: True,
                   Direction.LEFT: True,
                   Direction.UP: False,
                   Direction.DOWN: False
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

        self.left_lanes = [Lane(self, i, Direction.LEFT if self.horizontal else Direction.UP,
                                self.top + i * BLOCK_SIZE + i * LANE_DISPLACEMENT)
                           for i in range(left)]

        self.right_lanes = [Lane(self, i, Direction.RIGHT if self.horizontal else Direction.DOWN,
                                 self.top + i * BLOCK_SIZE + i * LANE_DISPLACEMENT +
                                 left * BLOCK_SIZE + left * LANE_DISPLACEMENT)
                            for i in range(right)]

        # Below the last left lane
        self.half = self.top + left * BLOCK_SIZE + (left - 1) * LANE_DISPLACEMENT
        # Below the last right lane
        self.bottom = self.top + (left + right) * BLOCK_SIZE + (
                left + right - 1) * LANE_DISPLACEMENT


class Lane:
    def __init__(self,
                 road: Road,
                 num: int,
                 direction: Direction,
                 top: int) -> None:
        self.road = road
        self.num = num
        self.top = top
        self.direction = direction
        self.segments = []


class LaneSegment:
    def __init__(self,
                 lane: Lane,
                 begin: int,
                 end: int) -> None:
        self.lane = lane
        self.begin = begin
        self.end = end
        self.end_crossing = None
        self.length = abs(self.end - self.begin)
        self.num = None

    def __str__(self):
        return f"{self.lane.road.name}:{self.lane.num}"


class CrossingSegment:
    def __init__(self,
                 horiz_lane: Lane,
                 vert_lane: Lane) -> None:
        self.horiz_lane = horiz_lane
        self.vert_lane = vert_lane
        self.right: LaneSegment | CrossingSegment = None
        self.left: LaneSegment | CrossingSegment = None
        self.up: LaneSegment | CrossingSegment = None
        self.down: LaneSegment | CrossingSegment = None
        self.length = BLOCK_SIZE
        self.horiz_num = None
        self.vert_num = None

    def get_road(self, direction: Direction, opposite: bool = False):
        if direction == Direction.RIGHT or Direction.LEFT and not opposite:
            return self.horiz_lane.road
        else:
            return self.horiz_lane.road

    def __str__(self):
        return f"({self.horiz_lane.road.name}:{self.horiz_lane.num}, {self.vert_lane.road.name}:{self.vert_lane.num})"


class Goal:
    def __init__(self, lane_segment: LaneSegment, loc: int, color: Color) -> None:
        self.lane_segment = lane_segment
        self.loc = loc
        self.color = color

        self.pos = Point(self.loc, self.lane_segment.lane.top) if self.lane_segment.lane.road.horizontal \
            else Point(self.lane_segment.lane.top, self.loc)
