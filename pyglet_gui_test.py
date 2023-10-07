from game_model.constants import *
from game_model.helper_functions import create_segments
from game_model.road_network import Road
from gui.pyglet_class_test import CarsWindowTest

if __name__ == '__main__':
    road_bottom = Road("bottom", True, 0, 1, 0)
    road_right = Road("right", False, WINDOW_SIZE - BLOCK_SIZE, 0, 1)
    road_top = Road("top", True, WINDOW_SIZE - BLOCK_SIZE, 0, 1)
    road_left = Road("left", False, 0, 1, 0)

    road_1 = Road("r1", True, 150, 3, 3)
    road_2 = Road("r2", True, 500, 3, 3)
    road_3 = Road("r3", False, 150, 3, 3)
    road_4 = Road("r4", False, 500, 3, 3)

    roads = [road_top, road_bottom, road_left, road_right, road_1, road_2, road_3, road_4]
    players = 1

    segments = create_segments(roads)
    CarsWindowTest(roads)
