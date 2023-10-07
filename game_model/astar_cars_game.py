import random

import numpy as np

from game_model.car import Car
from game_model.road_network import Goal, Road, Direction, Point, CrossingSegment, LaneSegment, Problem, clock_wise
from game_model.helper_functions import create_random_car, overlap, create_segments, dist, reached_goal
from constants import *


class AstarCarsGame:
    def __init__(self, roads: list[Road], players: int, cars: list[Car] = None):
        super().__init__()
        self.roads = roads
        self.segments = create_segments(roads)
        self.players = players

        self.cars = cars

        self.n_actions = 3

        # init display
        self.gui = None
        self.moved = True

        self.reset()

    def reset(self):
        # init game state
        self.scores: list[int] = [0] * self.players
        self.goals: list[Goal] = [None] * self.players
        self.useless_iterations: list[int] = [0] * self.players
        self.cars = []
        for i in range(self.players):
            self.cars.append(create_random_car(self.roads, self.cars))
        for i in range(self.players):
            self._place_goal(i)

    def _place_goal(self, player):
        self.useless_iterations[player] = 0

        road = random.choice(self.roads)
        lane = random.choice(road.right_lanes + road.left_lanes)
        lane_segment = random.choice([seg for seg in lane.segments if isinstance(seg, LaneSegment)])
        if self.goals[player] is None:
            self.goals[player] = Goal(lane_segment, self.cars[player].color)
        else:
            self.goals[player].lane_segment = lane_segment
            self.goals[player].update_position()

    def play_step(self, player, actions):
        self.useless_iterations[player] += 1
        car = self.cars[player]
        game_over = False

        # 1. Execute selected action
        moved = self._move(player, actions)  # update the head

        # 2. Check if the action was possible
        if isinstance(moved, Problem):
            game_over = True
            car.dead = True
            print("Crash:")
            print(moved)
            print(car)
            return game_over, self.scores[player]

        # 3. place new goal if the goal is reached
        # if overlap(self.cars[player].pos, self.cars[player].w, self.cars[player].h,
        #            self.goals[player].pos, BLOCK_SIZE, BLOCK_SIZE):
        if reached_goal(car, self.goals[player]):
            self.scores[player] += 1
            self._place_goal(player)
            print(f"Player {player}: Score {self.scores[player]}")

        # 6. Player won!
        if self.scores[player] > 100:
            game_over = True
            car.dead = True
            return game_over, self.scores[player]

        # 7. return game over and score
        return game_over, self.scores[player]

    def _move(self, player, actions):
        car = self.cars[player]
        idx = clock_wise.index(car.direction)
        action_worked = True
        match actions["turn"]:
            case 1:
                match car.res[-1]["seg"]:
                    case LaneSegment():
                        print("Conflict between game and controller! ")
                        pass
                        # action_worked = car.change_lane(1)
                        # if not action_worked:
                        #     return action_worked
                    case CrossingSegment():
                        next_idx = (idx + 1) % 4
                        new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u ->
                        action_worked = car.turn(new_dir)
                        if not action_worked:
                            return action_worked
            case 2:
                match car.res[-1]["seg"]:
                    case LaneSegment():
                        print("Conflict between game and controller! ")
                        pass
                        # action_worked = car.change_lane(-1)
                        # if not action_worked:
                        #     return action_worked
                    case CrossingSegment():
                        next_idx = (idx - 1) % 4
                        new_dir = clock_wise[next_idx]  # left turn u -> l -> d -> r ->
                        action_worked = car.turn(new_dir)
                        if not action_worked:
                            return action_worked

        action_worked = car.change_speed(actions["accelerate"])  # slow down
        if not action_worked:
            return action_worked

        action_worked = car.move()
        return action_worked

    def is_collision(self, player, pt=None) -> bool:
        car = self.cars[player]
        if pt is None:
            pt = self.cars[player].pos
        # hits boundary
        if pt.x > WINDOW_SIZE - 1 or pt.x < 0 or pt.y > WINDOW_SIZE - 1 or pt.y < 0:
            return True
        # hits other cars
        if any([overlap(pt,
                        car.w,
                        car.h,
                        self.cars[i].pos,
                        self.cars[i].w,
                        self.cars[i].h)
                for i in range(self.players) if i != player]):
            return True
        return False
