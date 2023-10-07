from game_model.constants import *
from controller.astar_car_controller import AstarCarController
from game_model.game_model import AstarCarsGame
from game_model.road_network import Road
from gui.pyglet_gui import CarsWindow


def main(players, roads, eval=5, manual=False):

    game = AstarCarsGame(players=players, roads=roads)
    controllers = [AstarCarController(game=game, player=i) for i in range(players)]

    if eval > 0:
        print("\n\nEvaluating\n\n")
        CarsWindow(game, controllers, eval, manual=manual)


if __name__ == '__main__':
    fn = "cars_model_10"

    players = 5

    road_bottom = Road("bottom", True, 0, 1, 0)
    road_right = Road("right", False, WINDOW_SIZE - BLOCK_SIZE, 0, 1)
    road_top = Road("top", True, WINDOW_SIZE - BLOCK_SIZE, 0, 1)
    road_left = Road("left", False, 0, 1, 0)

    road_1 = Road("r1", True, 150, 3, 3)
    road_2 = Road("r2", True, 500, 3, 3)
    road_3 = Road("r3", False, 150, 3, 3)
    road_4 = Road("r4", False, 500, 3, 3)

    roads = [road_top, road_bottom, road_left, road_right, road_1, road_2, road_3, road_4]

    main(players=players,
         roads=roads,
         eval=5,
         manual=False)

    # road_1 = Road("r1", True, 150, 3, 0)
    # road_2 = Road("r2", True, 500, 0, 3)
    # road_3 = Road("r3", False, 150, 3, 0)
    # road_4 = Road("r4", False, 500, 3, 3)
    #
    # roads = [road_1, road_2, road_3, road_4]
    #
    # main(players=players,
    #      roads=roads,
    #      eval=5,
    #      manual=False)
