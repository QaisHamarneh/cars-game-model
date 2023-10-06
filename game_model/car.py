import numpy as np
from pygame import Color

from constants import *
from game_model.road_network import LaneSegment, true_direction, Problem, CrossingSegment, Direction, Point, Road, \
    horiz_direction, right_direction


class Car:
    def __init__(self,
                 name: str,
                 loc: int,
                 segment: LaneSegment,
                 speed: int,
                 size: int,
                 color: Color,
                 roads: list[Road]) -> None:
        assert 0 <= loc <= segment.length, \
            f"Car {name}'s position is outside the window. WINDOW_SIZE = {WINDOW_SIZE}"

        self.name = name
        self.speed = speed
        self.size = size
        self.color = color
        self.roads = roads
        self.dead = False
        self.direction = segment.lane.direction

        self.res: list = [{"seg": segment, "dir": self.direction, "turn": False}]
        self.loc = loc

        self.pos = Point(0, 0)
        self.w = 0
        self.h = 0
        self._update_position()

    def move(self):
        # Within the lane

        self.loc += (1 if true_direction[self.res[0]["dir"]] else -1) * self.speed

        while abs(self.loc) + self.speed + self.size >= sum([seg["seg"].length for seg in self.res]):
            next_seg = self.get_next_segment()
            if next_seg is None:
                return Problem.NO_NEXT_SEGMENT
            self.res.append({"seg": next_seg, "dir": self.direction, "turn": False})

        while abs(self.loc) > self.res[0]["seg"].length:
            self.loc = np.sign(self.loc) * (abs(self.loc) - self.res[0]["seg"].length)
            self.res.pop(0)
        if self.res[0]["turn"]:
            self.loc = 0
            self.res[0]["turn"] = False

        self._update_position()
        return True

    def get_next_segment(self, direction=None) -> LaneSegment | CrossingSegment:
        if direction is None:
            direction = self.direction

        if isinstance(self.res[-1]["seg"], LaneSegment):
            return self.res[-1]["seg"].end_crossing
        else:
            return self.res[-1]["seg"].connected_segments[direction]

    def turn(self, new_direction):

        if isinstance(self.res[-1]["seg"], CrossingSegment):
            self.direction = new_direction
            self.res[-1]["dir"] = self.direction
            self.res[-1]["turn"] = True
            return True

    def change_speed(self, speed_diff):
        if self.speed == 0 and speed_diff < 0:
            return Problem.SLOWER_WHILE_0
        if self.speed == MAX_SPEED and speed_diff > 0:
            return Problem.FASTER_WHILE_MAX
        self.speed += speed_diff
        return True

    def get_adjacent_lane_segment(self, lane_segment: LaneSegment, lane_diff) -> LaneSegment:
        actual_lane_diff = (-1 if right_direction[self.direction] else 1) * lane_diff
        num = lane_segment.lane.num
        lanes = lane_segment.lane.road.right_lanes if right_direction[self.direction] \
            else lane_segment.lane.road.left_lanes
        if 0 <= num + actual_lane_diff < len(lanes):
            current_seg_num = self.res[0]["seg"].num
            return lanes[num + actual_lane_diff].segments[current_seg_num]
        return None

    def change_lane(self, lane_diff):
        segment = self.res[0]["seg"]
        if isinstance(segment, LaneSegment):
            next_lane_seg = self.get_adjacent_lane_segment(segment, lane_diff)
            if next_lane_seg is not None:
                self.res.append({"seg": next_lane_seg, "dir": self.direction})
                self._update_position()
                return True
        return Problem.NO_ADJACENT_LANE

    def _update_position(self):
        """ Returns the bottom left corner of the car """
        seg, direction = self.res[0]["seg"], self.res[0]["dir"]
        lane_seg = isinstance(seg, LaneSegment)
        road = seg.lane.road if lane_seg \
            else (seg.horiz_lane.road if horiz_direction[direction] else seg.vert_lane.road)

        if lane_seg:
            seg_begin = seg.begin
        if road.horizontal:
            if not lane_seg:
                seg_begin = seg.vert_lane.top if true_direction[direction] else seg.vert_lane.top + BLOCK_SIZE
            self.pos.y = seg.lane.top if lane_seg else seg.horiz_lane.top
            self.pos.x = seg_begin + self.loc - (0 if true_direction[direction] else self.size)
            self.w = self.size
            self.h = BLOCK_SIZE
        else:
            if not lane_seg:
                seg_begin = seg.horiz_lane.top if true_direction[direction] else seg.horiz_lane.top + BLOCK_SIZE
            self.pos.x = seg.lane.top if lane_seg else seg.vert_lane.top
            self.pos.y = seg_begin + self.loc - (0 if true_direction[direction] else self.size)
            self.w = BLOCK_SIZE
            self.h = self.size
