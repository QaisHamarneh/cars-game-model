from constants import *
from cars_game import CarsGame
from helper_classes import Road, Direction, Car, create_random_car
import pygame

if __name__ == '__main__':
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
    car_3 = Car("C", 100, road_3, 1, Direction.DOWN, 20, 40, 1, COLORS[3])
    car_4 = Car("D", 800, road_4, 2, Direction.UP, 20, 40, 1, COLORS[5])
    # cars=[car_1, car_2, car_3, car_4]
    cars = []
    for i in range(4):
        cars.append(create_random_car(roads, cars))

    game = CarsGame(players=4, cars=cars, roads=roads, render=True)
    # game loop
    pause = False
    for epi in range(20):
        game.reset()
        game_over = [False] * len(cars)
        scores = [0] * len(cars)
        while not all(game_over):
            action = [0] * 5
            action[0] = 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        action[0] = 0
                        action[1] = 1
                    elif event.key == pygame.K_DOWN:
                        action[0] = 0
                        action[2] = 1
                    elif event.key == pygame.K_RIGHT:
                        action[0] = 0
                        action[3] = 1
                    elif event.key == pygame.K_LEFT:
                        action[0] = 0
                        action[4] = 1
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            pause = not pause
            

            if not pause:
                if not game_over[0]:
                    reward, game_over[0], scores[0] = game.play_step(0, action)
                action = [0] * 5
                action[0] = 1
                for player in range(1, len(cars)):
                    if not game_over[player]:
                        reward, game_over[player], scores[player] = game.play_step(player, action)
                        print(f'reward {player} reward {reward} game_over {game_over[0]} scores {scores[0]}')
        
        print(f'Max Score {max(scores)}')
        
        
    pygame.quit()