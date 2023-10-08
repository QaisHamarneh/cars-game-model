import numpy as np
from pygame import Color

from game_model.constants import *
from game_model.road_network import LaneSegment, true_direction, Problem, CrossingSegment, Point, Road, \
    horiz_direction, right_direction, Segment


class Car:
    def __init__(self,
                 name: str,
                 loc: int,
                 segment: LaneSegment,
                 speed: int,
                 size: int,
                 color: Color,
                 max_speed: int) -> None:

        self.name = name
        self.speed = speed
        self.size = size
        self.color = color
        self.dead = False
        self.direction = segment.lane.direction
        self.loc = loc
        self.max_speed = max_speed

        self.claim: list = []
        self.res: list = [{"seg": segment,
                           "dir": self.direction,
                           "turn": False,
                           "begin": self.loc,
                           "end": (1 if true_direction[self.direction] else -1) * (self.loc + self.size + self.speed)}]

        segment.cars.append(self)
        self.pos = Point(0, 0)
        # For gui only
        self.w = 0
        self.h = 0
        self._update_position()

    def move(self):
        # Within the lane

        self.loc += (1 if true_direction[self.res[0]["dir"]] else -1) * self.speed
        if isinstance(self.res[-1]["seg"], LaneSegment):
            end = np.sign(self.loc) * (
                    abs(self.loc) + self.get_braking_distance() -
                    sum([self.res[i]["seg"].length for i in range(len(self.res) - 1)]))
            self.res[-1]["end"] = min(self.res[-1]["seg"].length, end)

        while abs(self.loc) + self.get_braking_distance() >= sum([seg["seg"].length for seg in self.res]):
            next_seg = self.get_next_segment()
            if next_seg is None:
                print("Problem.NO_NEXT_SEGMENT")
                return Problem.NO_NEXT_SEGMENT
            elif isinstance(next_seg, LaneSegment):
                extra = np.sign(self.loc) * (
                            abs(self.loc) + self.get_braking_distance() - sum([seg["seg"].length for seg in self.res]))
                next_seg_info = {"seg": next_seg,
                                 "dir": self.direction,
                                 "turn": False,
                                 "begin": 0,
                                 "end": extra}
                self.res.append(next_seg_info)
                next_seg.cars.append(self)
            else:
                next_seg_info = {"seg": next_seg,
                                 "dir": self.direction,
                                 "turn": False,
                                 "begin": 0,
                                 "end": (1 if true_direction[self.direction] else -1) * BLOCK_SIZE}
                self.res.append(next_seg_info)
                next_seg.cars.append(self)

        while abs(self.loc) > self.res[0]["seg"].length:
            self.loc = np.sign(self.loc) * (abs(self.loc) - self.res[0]["seg"].length)
            seg_info = self.res.pop(0)
            seg_info["seg"].cars.remove(self)
        if self.res[0]["turn"]:
            self.loc = 0
            self.res[0]["turn"] = False

        if isinstance(self.res[0]["seg"], LaneSegment):
            self.res[0]["begin"] = self.loc

        # txt = f"loc: {self.loc} "
        # for seg in self.res:
        #     txt += f"seg: {seg['seg']} {seg['begin']}//{seg['end']} "
        # print(txt)
        self._update_position()
        return True

    def get_next_segment(self, direction=None) -> Segment:
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
        self.speed = max(min(self.speed + speed_diff, self.max_speed), 0)
        return True

    def get_adjacent_lane_segment(self, lane_diff, lane_segment: LaneSegment = None) -> LaneSegment:
        if lane_segment is None:
            lane_segment = self.res[0]["seg"]
        actual_lane_diff = (-1 if right_direction[self.direction] else 1) * lane_diff
        num = lane_segment.lane.num
        lanes = lane_segment.lane.road.right_lanes if right_direction[self.direction] \
            else lane_segment.lane.road.left_lanes
        if 0 <= num + actual_lane_diff < len(lanes):
            current_seg_num = self.res[0]["seg"].num
            return lanes[num + actual_lane_diff].segments[current_seg_num]
        return None

    def change_lane(self, lane_diff):

        if len(self.res) == 1 and isinstance(self.res[0]["seg"], LaneSegment):
            next_lane_seg = self.get_adjacent_lane_segment(lane_diff)
            if next_lane_seg is not None:
                next_seg = {"seg": next_lane_seg,
                            "dir": next_lane_seg.lane.direction,
                            "turn": False,
                            "begin": self.res[0]["begin"],
                            "end": self.res[0]["end"]}
                self.res[0] = next_seg
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
            # BLOCK_SIZE // 6 for the triangle
            self.w = self.size - BLOCK_SIZE // 6
            self.h = BLOCK_SIZE
        else:
            if not lane_seg:
                seg_begin = seg.horiz_lane.top if true_direction[direction] else seg.horiz_lane.top + BLOCK_SIZE
            self.pos.x = seg.lane.top if lane_seg else seg.vert_lane.top
            self.pos.y = seg_begin + self.loc - (0 if true_direction[direction] else self.size)
            # BLOCK_SIZE // 6 for the triangle
            self.w = BLOCK_SIZE
            self.h = self.size - BLOCK_SIZE // 6

    def get_center(self):
        if horiz_direction[self.res[0]["dir"]]:
            return Point(self.pos.x + self.size // 2, self.pos.y + BLOCK_SIZE // 2)
        else:
            return Point(self.pos.x + BLOCK_SIZE // 2, self.pos.y + self.size // 2)

    def get_braking_distance(self):
        # braking = self.speed * (self.speed + 1) // 2
        braking = self.speed**2
        # BLOCK_SIZE // 10 additional distance when speed = 0
        return self.size + braking + BLOCK_SIZE // 10
