from constants import *
from game_model.cars_game import CarsGame
from game_model.road_network import Road, LaneSegment, CrossingSegment, Problem, Point
import pygame

from game_model.helper_functions import create_random_car, create_segments





if __name__ == '__main__':
    road_top = Road("top", True, 0, 0, 1)
    road_bottom = Road("bottom", True, WINDOW_SIZE - BLOCK_SIZE, 1, 0)
    road_left = Road("left", False, 0, 1, 0)
    road_right = Road("right", False, WINDOW_SIZE - BLOCK_SIZE, 0, 1)

    road_1 = Road("r1", True, 150, 3, 3)
    road_2 = Road("r2", True, 500, 3, 3)
    road_3 = Road("r3", False, 150, 3, 3)
    road_4 = Road("r4", False, 500, 3, 3)

    roads = [road_top, road_bottom, road_left, road_right, road_1, road_2, road_3, road_4]

    create_segments(roads)

    print(get_segment(Point(160, 0), roads))
    print(get_segment(Point(200, 0), roads))
    print(get_segment(Point(0, 0), roads))
    print(get_segment(Point(600, 0), roads))
    print(get_segment(Point(160, 160), roads))
    print(get_segment(Point(200, 200), roads))
    print(get_segment(Point(0, 140), roads))
    print(get_segment(Point(600, 600), roads))
    # seg = road_bottom.left_lanes[0].segments[0]
    # txt = ""
    # while seg is not None:
    #     if isinstance(seg, LaneSegment):
    #         txt += f"{seg.lane.road.name}:{seg.lane.num} "
    #         seg = seg.end_crossing
    #     else:
    #         txt += f"{seg.vert_lane.road.name}:{seg.vert_lane.num},{seg.horiz_lane.road.name}:{seg.horiz_lane.num} "
    #         seg = seg.up
    # print(txt)
