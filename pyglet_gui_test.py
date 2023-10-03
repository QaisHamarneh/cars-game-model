from constants import *
from game_model.cars_game import CarsGame
from game_model.road_network import Road
from gui.pyglet_class import CarsWindow
from learning_agent.cars_agent import CarAgent

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
    players = 1

    game = CarsGame(players=players, roads=roads)
    agents = [CarAgent(game=game, player=i, file_name="") for i in range(players)]
    CarsWindow(game, agents, 5, manual=True)
