import random
import string

import numpy as np

from constants import *
from game_model.car import Car
from game_model.road_network import Direction, Point, Road, CrossingSegment, LaneSegment, true_direction, Goal


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


def create_random_car(roads: list[Road], cars) -> Car:
    name = random.choice([char for char in string.ascii_uppercase if not any([car.name == char for car in cars])])
    color = random.choice([color for color in COLORS if not any([car.color == color for car in cars])])

    road = random.choice(roads)
    lane = random.choice(road.right_lanes + road.left_lanes)
    # lane_segment = random.choice([seg for seg in lane.segments
    #                               if isinstance(seg, LaneSegment) and not any([car.res == seg for car in cars])])
    lane_segment = random.choice([seg for seg in lane.segments if isinstance(seg, LaneSegment)])

    # speed = random.randint(BLOCK_SIZE // 2, MAX_SPEED)
    speed = random.randint(3, 6)
    speed = max(0.2, random.random()) * speed
    size = random.randint(BLOCK_SIZE // 2, 9 * BLOCK_SIZE // 10)
    loc = 0

    return Car(name=name,
               loc=loc,
               segment=lane_segment,
               speed=speed,
               size=size,
               color=color,
               roads=roads)


def create_segments(roads: list[Road]):
    roads.sort(key=lambda r: r.top)
    segments = []
    last_horiz = 0
    for horiz_road in roads:
        if horiz_road.horizontal:
            if last_horiz > horiz_road.top:
                print(f"\nRoad {horiz_road.name} overlaps with the previous road")
                return None
            last_vert = 0
            for vert_road in roads:
                if not vert_road.horizontal:
                    if last_vert > vert_road.top:
                        print(f"\nRoad {vert_road.name} {vert_road.top} overlaps with previous road {last_vert}")
                        return None

                    # Starting with lanes:
                    for horiz_lane in horiz_road.right_lanes + horiz_road.left_lanes:
                        # There horizontal exist a lane segment:
                        for vert_lane in vert_road.right_lanes + vert_road.left_lanes:
                            horiz_lane_segment = None
                            vert_lane_segment = None
                            if vert_road.top > last_vert and \
                                    (vert_lane.num == 0 and
                                     (vert_lane.direction == Direction.DOWN or len(vert_road.right_lanes) == 0)):
                                horiz_lane_segment = LaneSegment(horiz_lane, last_vert, vert_road.top) \
                                    if true_direction[horiz_lane.direction] \
                                    else LaneSegment(horiz_lane, vert_road.top, last_vert)
                            if horiz_road.top > last_horiz and \
                                    (horiz_lane.num == 0 and
                                     (horiz_lane.direction == Direction.RIGHT or len(horiz_road.right_lanes) == 0)):
                                vert_lane_segment = LaneSegment(vert_lane, last_horiz, horiz_road.top) \
                                    if true_direction[vert_lane.direction] \
                                    else LaneSegment(vert_lane, horiz_road.top, last_horiz)

                            if horiz_lane_segment is not None:
                                horiz_lane.segments.append(horiz_lane_segment)
                                horiz_lane_segment.num = len(horiz_lane.segments) - 1
                                segments.append(horiz_lane_segment)
                            if vert_lane_segment is not None:
                                vert_lane.segments.append(vert_lane_segment)
                                vert_lane_segment.num = len(vert_lane.segments) - 1
                                segments.append(vert_lane_segment)

                            crossing_segment = CrossingSegment(horiz_lane, vert_lane)
                            horiz_lane.segments.append(crossing_segment)
                            vert_lane.segments.append(crossing_segment)
                            crossing_segment.horiz_num = len(horiz_lane.segments) - 1
                            crossing_segment.vert_num = len(vert_lane.segments) - 1
                            segments.append(crossing_segment)

                    last_vert = vert_road.bottom

            last_horiz = horiz_road.bottom

    for road in roads:
        for lane in road.right_lanes + road.left_lanes:
            if true_direction[lane.direction]:
                for i in range(len(lane.segments) - 1):
                    match lane.segments[i]:
                        case LaneSegment():
                            lane.segments[i].end_crossing = lane.segments[i + 1]
                        case CrossingSegment():
                            if lane.direction == Direction.RIGHT:
                                lane.segments[i].connected_segments[Direction.RIGHT] = lane.segments[i + 1]
                                # if isinstance(lane.segments[i + 1], CrossingSegment):
                                #     lane.segments[i + 1].left = lane.segments[i]
                            elif lane.direction == Direction.UP:
                                lane.segments[i].connected_segments[Direction.UP] = lane.segments[i + 1]
                                # if isinstance(lane.segments[i + 1], CrossingSegment):
                                #     lane.segments[i + 1].down = lane.segments[i]
            else:
                for j in range(1, len(lane.segments)):
                    match lane.segments[j]:
                        case LaneSegment():
                            lane.segments[j].end_crossing = lane.segments[j - 1]
                        case CrossingSegment():
                            if lane.direction == Direction.LEFT:
                                lane.segments[j].connected_segments[Direction.LEFT] = lane.segments[j - 1]
                                # if isinstance(lane.segments[j - 1], CrossingSegment):
                                #     lane.segments[j - 1].right = lane.segments[j]
                            elif lane.direction == Direction.DOWN:
                                lane.segments[j].connected_segments[Direction.DOWN] = lane.segments[j - 1]
                                # if isinstance(lane.segments[j - 1], CrossingSegment):
                                #     lane.segments[j - 1].up = lane.segments[j]

    return segments
