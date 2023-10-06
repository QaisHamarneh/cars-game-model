import random

import numpy as np

from game_model.car import Car
from game_model.road_network import Goal, Road, Direction, Point, CrossingSegment, LaneSegment, Problem, clock_wise
from game_model.helper_functions import create_random_car, overlap, create_segments, dist
from constants import *


class CarsGame:
    def __init__(self, roads: list[Road], players: int, cars: list[Car] = None, fixed=True):
        super().__init__()
        self.roads = roads
        self.intersections = create_segments(roads)
        self.players = players

        self.cars = cars
        self.fixed = fixed

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
        if not self.fixed:
            self.cars = []
            for i in range(self.players):
                self.cars.append(create_random_car(self.roads, self.cars))
        else:
            car = Car("A", 0, self.roads[4].right_lanes[0].segments[1], 10, 20, COLORS[0], self.roads)
            self.cars = [car]
        for i in range(self.players):
            self._place_goal(i)

    def _place_goal(self, player):
        self.useless_iterations[player] = 0
        car = self.cars[player]

        # if not self.fixed:
        #     road = random.choice(self.roads)
        #     lane = random.choice(road.right_lanes + road.left_lanes)
        #     lane_segment = random.choice([seg for seg in lane.segments if isinstance(seg, LaneSegment)])
        #     self.goals[player] = Goal(lane_segment, car.color)
        # else:
        self.goals[player] = Goal(self.roads[5].right_lanes[0].segments[-2], car.color)

    def play_step(self, player, action):
        self.useless_iterations[player] += 1
        car = self.cars[player]
        reward = 0
        game_over = False
        action_ind = action.index(1)

        # 2. move
        old_dist_to_food = dist(car.pos, self.goals[player].pos)
        moved = self._move(player, action_ind)  # update the head

        new_dist_to_food = dist(car.pos, self.goals[player].pos)

        # 3. check reward
        if isinstance(moved, Problem):
            reward = -10

        if moved == Problem.NO_NEXT_SEGMENT:
            # game_over = True
            # car.dead = True
            reward = -100
            # return reward, game_over, self.scores[player]

        # if new_dist_to_food <= old_dist_to_food:
        #     reward = int(old_dist_to_food - new_dist_to_food)
        # else:
        #     reward = -1

        # 4. check Collision
        # self.is_collision(player) or
        if self.is_collision(player) or self.useless_iterations[player] > WINDOW_SIZE * 10:
            game_over = True
            car.dead = True
            reward = 1000
            return reward, game_over, self.scores[player]

        # 5. place new food or just move
        if overlap(self.cars[player].pos, self.cars[player].w, self.cars[player].h,
                   self.goals[player].pos, BLOCK_SIZE, BLOCK_SIZE):
            self.scores[player] += 1
            reward = 1000
            self._place_goal(player)
            # if self.fixed:
            #     game_over = True
            #     return reward, game_over, self.scores[player]

        # 6. Player won!
        if self.scores[player] > 100:
            game_over = True
            car.dead = True
            reward = 100_000
            return reward, game_over, self.scores[player]

        # 7. return game over and score
        return reward, game_over, self.scores[player]

    def _move(self, player, action_ind):
        car = self.cars[player]

        idx = clock_wise.index(car.direction)
        action_worked = True
        match action_ind:
            case 1:
                match car.res:
                    case LaneSegment():
                        action_worked = car.change_lane(1)
                        if not action_worked:
                            return action_worked
                    case CrossingSegment():
                        next_idx = (idx + 1) % 4
                        new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u ->
                        action_worked = car.turn(new_dir)
                        if not action_worked:
                            return action_worked
            case 2:
                match car.res:
                    case LaneSegment():
                        action_worked = car.change_lane(-1)
                        if not action_worked:
                            return action_worked
                    case CrossingSegment():
                        next_idx = (idx - 1) % 4
                        new_dir = clock_wise[next_idx]  # left turn u -> l -> d -> r ->
                        action_worked = car.turn(new_dir)
                        if not action_worked:
                            return action_worked
            case 3:
                action_worked = car.change_speed(-1)  # slow down
                if not action_worked:
                    return action_worked
            case 4:
                action_worked = car.change_speed(1)  # speed up
                if not action_worked:
                    return action_worked
        if action_ind != 1 and action_ind != 2:
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

    def get_state(self, player):

        car = self.cars[player]

        idx = clock_wise.index(car.direction)

        dir_r = car.direction == Direction.RIGHT
        dir_l = car.direction == Direction.LEFT
        dir_u = car.direction == Direction.UP
        dir_d = car.direction == Direction.DOWN

        forward_possible = car.loc + car.speed < car.res.length or car.get_next_segment() is not None
        right_possible = isinstance(car.res, CrossingSegment) and \
                         car.get_next_segment(clock_wise[(idx + 1) % 4]) is not None
        left_possible = isinstance(car.res, CrossingSegment) and \
                        car.get_next_segment(clock_wise[(idx + 1) % 4]) is not None

        right_lane_possible = isinstance(car.res, LaneSegment) and \
                         car.get_adjacent_lane_segment(1) is not None
        left_lane_possible = isinstance(car.res, LaneSegment) and \
                         car.get_adjacent_lane_segment(-1) is not None

        state = [
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            isinstance(car.res, CrossingSegment),
            forward_possible,
            right_possible,
            left_possible,
            right_lane_possible,
            left_lane_possible,

            # Food location
            self.goals[player].pos.x - car.pos.x,  # food left
            self.goals[player].pos.y - car.pos.y,  # food up
        ]

        return np.array(state, dtype=int)
