from pygame import Color

from constants import *
from game_model.road_network import LaneSegment, true_direction, Problem, CrossingSegment, Direction, Point, Road, \
    direction_axis


class Car:
    def __init__(self,
                 name: str,
                 loc: int,
                 lane_segment: LaneSegment,
                 speed: int,
                 size: int,
                 acceleration: int,
                 color: Color) -> None:
        assert 0 <= loc <= lane_segment.length, \
            f"Car {name}'s position is outside the window. WINDOW_SIZE = {WINDOW_SIZE}"

        self.name = name
        self.speed = speed
        self.size = size
        self.acceleration = acceleration
        self.color = color
        self.dead = False
        self.direction = lane_segment.lane.direction

        self.res: LaneSegment | CrossingSegment = lane_segment
        self.loc = loc
        self.lane_change_counter = 0

        self.pos = Point(0, 0)
        self.w = 0
        self.h = 0
        self._update_position()

    def change_acceleration(self, speed_diff):
        if self.speed == 0 and speed_diff < 0:
            return Problem.SLOWER_WHILE_0
        if self.speed == MAX_SPEED and speed_diff > 0:
            return Problem.FASTER_WHILE_MAX
        self.speed += speed_diff
        return True

    def move(self, roads):
        # Within the lane
        self.pos.x += direction_axis[self.direction][0] * self.speed
        self.pos.y += direction_axis[self.direction][1] * self.speed

        # self.loc += (1 if true_direction[self.direction] else -1) * self.speed

        self.res = self.get_segment(roads)
        if isinstance(self.res, Problem):
            return self.res
        # if self.loc > self.res.length:
        #     next_seg = self._get_next_segment()
        #     if next_seg is None:
        #         return Problem.NO_NEXT_SEGMENT
        #     self.loc -= self.res.length
        #     self.res = next_seg
        # elif self.loc < 0:
        #     next_seg = self._get_next_segment()
        #     if next_seg is None:
        #         return Problem.NO_NEXT_SEGMENT
        #     self.loc = next_seg.length + self.loc
        #     self.res = next_seg

        # self._update_position()
        return True

    def _get_next_segment(self) -> LaneSegment | CrossingSegment:
        if isinstance(self.res, LaneSegment):
            return self.res.end_crossing
        else:
            if self.direction == Direction.RIGHT:
                return self.res.right
            if self.direction == Direction.LEFT:
                return self.res.left
            if self.direction == Direction.UP:
                return self.res.up
            if self.direction == Direction.DOWN:
                return self.res.down

    def turn(self, new_direction):
        if isinstance(self.res, CrossingSegment):
            self.direction = new_direction
            self.pos.y = self.res.horiz_lane.top
            self.pos.x = self.res.vert_lane.top
            if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
                self.w = self.size
                self.h = BLOCK_SIZE
            else:
                self.w = BLOCK_SIZE
                self.h = self.size

            # self.loc = 0 if true_direction[self.direction] else BLOCK_SIZE
            # self._update_position()
            return True

    def _get_adjacent_lane_segment(self, lane_diff) -> LaneSegment:
        num = self.res.lane.num
        lanes = self.res.lane.road.right_lanes if true_direction[self.direction] \
            else self.res.lane.road.left_lanes
        if 0 <= num + lane_diff < len(lanes):
            current_seg_num = self.res.num
            self.res = lanes[num + lane_diff].segments[current_seg_num]
            return True
        return False

    def change_lane(self, lane_diff):
        if isinstance(self.res, LaneSegment):
            if self._get_adjacent_lane_segment((1 if true_direction[self.direction] else -1) * lane_diff):
                # self._update_position()
                if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
                    self.pos.y = self.res.lane.top
                else:
                    self.pos.x = self.res.lane.top
                return True
        return Problem.NO_ADJACENT_LANE

    def _update_position(self):
        """ Returns the top left corner of the car """
        seg = self.res
        self.pos.y = (seg.lane.top if isinstance(seg, LaneSegment) else seg.horiz_lane.top)
        self.pos.x = (seg.begin if isinstance(seg, LaneSegment) else seg.vert_lane.top) + self.loc
        self.w = self.size if self.direction == Direction.RIGHT or self.direction == Direction.LEFT else BLOCK_SIZE
        self.h = BLOCK_SIZE if self.direction == Direction.RIGHT or self.direction == Direction.LEFT else self.size

    def get_segment(self, roads: list[Road]) -> LaneSegment | CrossingSegment:
        if self.pos.x < 0 or self.pos.x > WINDOW_SIZE:
            return Problem.NO_NEXT_SEGMENT
        if self.pos.y < 0 or self.pos.y > WINDOW_SIZE:
            return Problem.NO_NEXT_SEGMENT
        for road in roads:
            for lane in road.left_lanes + road.right_lanes:
                for seg in lane.segments:
                    if road.horizontal:
                        if isinstance(seg, LaneSegment):
                            if lane.top <= self.pos.y <= lane.top + BLOCK_SIZE \
                                    and seg.begin <= self.pos.x <= seg.end:
                                return seg
                        else:
                            if lane.top <= self.pos.y <= lane.top + BLOCK_SIZE \
                                    and seg.vert_lane.top <= self.pos.x <= seg.vert_lane.top + BLOCK_SIZE:
                                return seg
                    else:
                        if isinstance(seg, LaneSegment):
                            if lane.top <= self.pos.x <= lane.top + BLOCK_SIZE \
                                    and seg.begin <= self.pos.y <= seg.end:
                                return seg
                        else:
                            if lane.top <= self.pos.x <= lane.top + BLOCK_SIZE \
                                    and seg.horiz_lane.top <= self.pos.y <= seg.horiz_lane.top + BLOCK_SIZE:
                                return seg

    def __str__(self):
        txt = f"name {self.name}, "
        if isinstance(self.res, LaneSegment):
            txt += f"road {self.res.lane.road.name}, "
            txt += f"lane {self.res.lane.num}, "
        elif isinstance(self.res, CrossingSegment):
            txt += f"horiz road {self.res.horiz_lane.road.name}, "
            txt += f"vert road {self.res.vert_lane.road.name}, "
            txt += f"horiz lane {self.res.horiz_lane.num}, "
            txt += f"vert lane {self.res.vert_lane.num}, "
        txt += f"{self.direction}\n"
        txt += f"lane segments "
        txt += f'{self.res} length {self.res.length} '
        txt += "\n"
        # txt += f"loc {self.loc}, pos ({self.pos.x}, {self.pos.y}), speed {self.speed}\n" \
        txt += f"pos ({self.pos.x}, {self.pos.y}), speed {self.speed}\n" \
               f"__________________________________________________________"
        return txt

