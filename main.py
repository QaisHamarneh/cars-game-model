import pygame
from cars_agent import CarAgent
from cars_game import CarsGame
from helper_classes import Car, Direction, Road, create_random_car
from constants import *


def main(cars, file_name, roads=[], train=0, eval=5, rand=False, render=False):

    players = len(cars)
    game = CarsGame(players=players, cars=cars, roads=roads, render=render)

    agents = [CarAgent(game=game, player=i, file_name=file_name) for i in range(players)]
    
    if train > 0:
        print("\n\nTraining\n\n")
        for i in range(train):
            gameover = [False] * players
            while not all(gameover):
                for player in range(players):
                    if not gameover[player]:
                        gameover[player] = agents[player].train()

                if render:
                    # 1. collect user input
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()

            game.reset()

    if eval > 0:
        if train == 0 and not rand:
            for player in range(players):
                agents[player].load_model()
        game.activate_gui()
        print("\n\nEvaluating\n\n")
        pause = False
        scores = [0] * players
        for i in range(eval):
            gameover = [False] * players
            while not all(gameover):
                for player in range(players):
                    if not pause and not gameover[player]:
                        gameover[player], scores[player] = agents[player].eval(rand=rand)

                    # 1. collect user input
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                pause = not pause
                    
                if all(gameover):
                    print(f"Game {i}:")
                    for player in range(players):
                        print(f"player {player} score {scores[player]}")
            game.reset()


if __name__ == '__main__':
    players = 4
    fn = "cars_model_3"

    road_top = Road("top", True, 0, 0, 1)
    road_bottom = Road("bottom", True, WINDOW_SIZE - BLOCK_SIZE, 1, 0)
    road_left = Road("left", False, 0, 1, 0)
    road_right = Road("bottom", False, WINDOW_SIZE - BLOCK_SIZE, 0, 1)

    road_1 = Road("r1", True, 150, 3, 3)
    road_2 = Road("r2", True, 500, 3, 3)
    road_3 = Road("r3", False, 150, 3, 3)
    road_4 = Road("r4", False, 500, 3, 3)

    roads = [road_top, road_bottom, road_left, road_right, road_1, road_2, road_3, road_4]

    car_1 = Car("A", 100, road_1, 1, Direction.RIGHT, 20, 40, 1, COLORS[0])
    car_2 = Car("B", 800, road_1, 2, Direction.LEFT, 20, 40, 1, COLORS[1])
    car_3 = Car("C", 100, road_3, 1, Direction.DOWN, 20, 40, 1, COLORS[2])
    car_4 = Car("D", 800, road_4, 2, Direction.UP, 20, 40, 1, COLORS[3])
    # cars=[car_1, car_2, car_3, car_4]

    cars = []
    for i in range(4):
        cars.append(create_random_car(roads, cars))

    main(file_name=fn,  
         cars=cars,
         roads=roads, 
         train=0, eval=5, 
         rand=False, render=False)

