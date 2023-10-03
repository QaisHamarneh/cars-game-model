import random
import string

import numpy as np

from constants import *
from game_model.car import Car
from game_model.road_network import Direction, Point, Road, CrossingSegment, LaneSegment, true_direction


def dist(p1, p2):
    return np.linalg.norm([p1.x - p2.x, p1.y - p2.y])


def overlap(p1, w1, h1, p2, w2, h2):
    # If one rectangle is on left side of other
    if p1.x > p2.x + w2 or p2.x > p1.x + w1:
        return False

    # If one rectangle is above other
    if p1.y > p2.y + h2 or p2.y > p1.y + h1:
        return False

    return True


def pick_random_location(roads: list[Road]):
    road = random.choice(roads)
    lane = random.choice(road.left_lanes + road.right_lanes)
    lane_segment = random.choice(lane.segments)
    while isinstance(lane_segment, CrossingSegment):
        lane_segment = random.choice(lane.segments)

    speed = random.randint(BLOCK_SIZE // 2, BLOCK_SIZE)
    size = random.randint(BLOCK_SIZE // 2, 9 * BLOCK_SIZE // 10)
    loc = random.randint(0, lane_segment.length - size - speed)
    pos = lane_segment.begin + loc if true_direction[lane.direction] \
        else lane_segment.end - loc - size - speed
    p = Point(pos, lane.top) if road.horizontal \
        else Point(lane.top, pos)
    return road, lane_segment, size, speed, loc, p


def create_random_car(roads: list[Road], cars) -> Car:
    name = random.choice(string.ascii_uppercase)
    while any([car.name == name for car in cars]):
        name = random.choice(string.ascii_uppercase)
    color = random.choice(COLORS)
    while any([car.color == color for car in cars]):
        color = random.choice(COLORS)

    road, lane_segment, size, speed, loc, p = pick_random_location(roads)
    while any([overlap(p,
                       size + speed if road.horizontal else BLOCK_SIZE,
                       BLOCK_SIZE if road.horizontal else size + speed,
                       cars[i].pos, cars[i].w, cars[i].h)
               for i in range(len(cars))]):
        road, lane_segment, size, speed, loc, p = pick_random_location(roads)

    acceleration = random.choice([-1, 0, 1])

    return Car(name=name,
               loc=loc,
               lane_segment=lane_segment,
               speed=speed,
               acceleration=acceleration,
               size=size,
               color=color)


def create_segments(roads: list[Road]):
    roads.sort(key=lambda r: r.top)
    last_horiz = 0

    for horiz_road in roads:
        if horiz_road.horizontal:
            if last_horiz > horiz_road.top:
                print(f"\nRoad {horiz_road.name} overlaps with the previous road")
                return False
            last_vert = 0
            for vert_road in roads:
                if not vert_road.horizontal:
                    if last_vert > vert_road.top:
                        print(f"\nRoad {vert_road.name} {vert_road.top} overlaps with previous road {last_vert}")
                        return False

                    # Starting with lanes:
                    for horiz_lane in horiz_road.left_lanes + horiz_road.right_lanes:
                        # There horizontal exist a lane segment:
                        for vert_lane in vert_road.left_lanes + vert_road.right_lanes:
                            horiz_lane_segment = None
                            vert_lane_segment = None
                            if vert_road.top > last_vert and \
                                    (vert_lane.num == 0 and
                                     (vert_lane.direction == Direction.UP or len(vert_road.left_lanes) == 0)):
                                horiz_lane_segment = LaneSegment(horiz_lane, last_vert, vert_road.top)
                            if horiz_road.top > last_horiz and \
                                    (horiz_lane.num == 0 and
                                     (horiz_lane.direction == Direction.LEFT or len(horiz_road.left_lanes) == 0)):
                                vert_lane_segment = LaneSegment(vert_lane, last_horiz, horiz_road.top)

                            if horiz_lane_segment is not None:
                                horiz_lane.segments.append(horiz_lane_segment)
                                horiz_lane_segment.num = len(horiz_lane.segments) - 1
                            if vert_lane_segment is not None:
                                vert_lane.segments.append(vert_lane_segment)
                                vert_lane_segment.num = len(vert_lane.segments) - 1

                            crossing_segment = CrossingSegment(horiz_lane, vert_lane)
                            horiz_lane.segments.append(crossing_segment)
                            vert_lane.segments.append(crossing_segment)
                            crossing_segment.horiz_num = len(horiz_lane.segments) - 1
                            crossing_segment.vert_num = len(vert_lane.segments) - 1

                    last_v_lane = vert_road.right_lanes[-1].top if vert_road.right_lanes else vert_road.left_lanes[-1].top
                    last_vert = last_v_lane + BLOCK_SIZE

            last_h_lane = horiz_road.right_lanes[-1].top if horiz_road.right_lanes else horiz_road.left_lanes[-1].top
            last_horiz = last_h_lane + BLOCK_SIZE

    for road in roads:
        for lane in road.left_lanes + road.right_lanes:
            if true_direction[lane.direction]:
                for i in range(len(lane.segments) - 1):
                    match lane.segments[i]:
                        case LaneSegment():
                            lane.segments[i].end_crossing = lane.segments[i + 1]
                        case CrossingSegment():
                            if lane.direction == Direction.RIGHT:
                                lane.segments[i].right = lane.segments[i + 1]
                                if isinstance(lane.segments[i + 1], CrossingSegment):
                                    lane.segments[i + 1].left = lane.segments[i]
                            elif lane.direction == Direction.DOWN:
                                lane.segments[i].down = lane.segments[i + 1]
                                if isinstance(lane.segments[i + 1], CrossingSegment):
                                    lane.segments[i + 1].up = lane.segments[i]
            else:
                for i in range(1, len(lane.segments)):
                    match lane.segments[i]:
                        case LaneSegment():
                            lane.segments[i].end_crossing = lane.segments[i - 1]
                        case CrossingSegment():
                            if lane.direction == Direction.LEFT:
                                lane.segments[i].left = lane.segments[i - 1]
                                if isinstance(lane.segments[i - 1], CrossingSegment):
                                    lane.segments[i - 1].right = lane.segments[i]
                            elif lane.direction == Direction.UP:
                                lane.segments[i].up = lane.segments[i - 1]
                                if isinstance(lane.segments[i - 1], CrossingSegment):
                                    lane.segments[i - 1].down = lane.segments[i]

    return True

