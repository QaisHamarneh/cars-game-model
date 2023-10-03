import random

import numpy as np

from game_model.car import Car
from game_model.road_network import Goal, Road, Direction, Point, CrossingSegment, LaneSegment, Problem
from game_model.helper_functions import create_random_car, overlap, create_segments, dist
from constants import *


class CarsGame():

    def __init__(self, roads: list[Road], players: int, cars: list[Car] = None):
        super().__init__()
        self.roads = roads
        self.intersections = create_segments(roads)
        self.players = players
        self.cars = cars

        self.n_actions = 5

        # init display
        self.gui = None
        self.moved = True

        self.reset()

    def reset(self):
        # init game state
        self.scores: list[int] = [0] * self.players
        self.goals: list[Goal] = [None] * self.players
        self.useless_iterations: list[int] = [0] * self.players
        if self.cars is None:
            self.cars = []
            for i in range(self.players):
                self.cars.append(create_random_car(self.roads, self.cars))
        for i in range(self.players):
            self._place_goal(i)

    def _place_goal(self, player):
        self.useless_iterations[player] = 0

        car = self.cars[player]
        road = random.choice(self.roads)
        lane = random.choice(road.left_lanes + road.right_lanes)
        lane_segment = random.choice(lane.segments)
        while isinstance(lane_segment, CrossingSegment):
            lane_segment = random.choice(lane.segments)

        loc = random.randint(BLOCK_SIZE, WINDOW_SIZE - BLOCK_SIZE)
        p = Point(loc, lane.top) if lane.road.horizontal \
            else Point(lane.top, loc)
        while overlap(p, BLOCK_SIZE, BLOCK_SIZE, car.pos, car.w, car.h):
            road = random.choice(self.roads)
            lane = random.choice(road.left_lanes + road.right_lanes)
            lane_segment = random.choice(lane.segments)
            while isinstance(lane_segment, CrossingSegment):
                lane_segment = random.choice(lane.segments)
            loc = random.randint(BLOCK_SIZE, WINDOW_SIZE - BLOCK_SIZE)
            p = Point(loc, lane.top) if lane.road.horizontal \
                else Point(lane.top, loc)

        self.goals[player] = Goal(lane_segment, loc, car.color)

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
            reward -= 5

        if new_dist_to_food <= old_dist_to_food:
            reward += int(old_dist_to_food - new_dist_to_food) // 10
        else:
            reward -= 1

        # 4. check Collision
        if self.is_collision(player) or self.useless_iterations[player] > WINDOW_SIZE * 10:
            game_over = True
            car.dead = True
            reward -= 1000
            return reward, game_over, self.scores[player]

        # 5. place new food or just move
        if overlap(self.cars[player].pos, self.cars[player].w, self.cars[player].h,
                   self.goals[player].pos, BLOCK_SIZE, BLOCK_SIZE):
            self.scores[player] += 1
            reward += 10000
            self._place_goal(player)

        # 6. Player won!
        if self.scores[player] > 100:
            game_over = True
            car.dead = True
            reward += 1000_000
            return reward, game_over, self.scores[player]

        # 7. return game over and score
        return reward, game_over, self.scores[player]

    def _move(self, player, action_ind):
        car = self.cars[player]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]

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
                action_worked = car.change_acceleration(-1)  # slow down
                if not action_worked:
                    return action_worked
            case 4:
                action_worked = car.change_acceleration(1)  # speed up
                if not action_worked:
                    return action_worked
        if action_ind != 1 and action_ind != 2:
            action_worked = car.move(self.roads)
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

        dir_r = car.direction == Direction.RIGHT
        dir_l = car.direction == Direction.LEFT
        dir_u = car.direction == Direction.UP
        dir_d = car.direction == Direction.DOWN

        dist_front = WINDOW_SIZE
        dist_up = WINDOW_SIZE
        dist_down = WINDOW_SIZE

        if dir_r:
            for road in self.roads:
                if not road.horizontal:
                    dist_front = min(dist_front, road.top - car.pos.x) if road.top >= car.pos.x else dist_front
                else:
                    dist_up = min(dist_up, car.pos.y - road.half) if car.pos.y >= road.half else dist_up
                    dist_down = min(dist_down, road.bottom - car.pos.y) if road.bottom >= car.pos.y else dist_down
        if dir_l:
            for road in self.roads:
                if not road.horizontal:
                    dist_front = min(dist_front, car.pos.x - road.bottom) if car.pos.x >= road.bottom else dist_front
                else:
                    dist_up = min(dist_up, car.pos.y - road.top) if car.pos.y >= road.top else dist_up
                    dist_down = min(dist_down, road.half - car.pos.y) if road.half >= car.pos.y else dist_down
        if dir_u:
            for road in self.roads:
                if not road.horizontal:
                    dist_front = min(dist_front, car.pos.y - road.bottom) if car.pos.y >= road.bottom else dist_up
                else:
                    dist_up = min(dist_up, car.pos.x - road.top) if car.pos.x >= road.top else dist_up
                    dist_down = min(dist_down, road.half - car.pos.x) if road.half >= car.pos.x else dist_down
        if dir_d:
            for road in self.roads:
                if road.horizontal:
                    dist_front = min(dist_front, road.top - car.pos.y) if road.top >= car.pos.y else dist_front
                else:
                    dist_up = min(dist_up, car.pos.x - road.half) if car.pos.x >= road.half else dist_up
                    dist_down = min(dist_down, road.bottom - car.pos.x) if road.bottom >= car.pos.x else dist_down

        for other_car in self.cars:
            if other_car != car:
                if car.direction == Direction.RIGHT or car.direction == Direction.LEFT:
                    if other_car.pos.y == car.pos.y:
                        dist_front = min(dist_front, other_car.pos.x - car.pos.x) if other_car.pos.x >= car.pos.x \
                            else dist_front
                    elif overlap(other_car.pos, other_car.w, other_car.h,
                                 Point(car.pos.x, car.pos.y + BLOCK_SIZE), car.w, car.h):
                        dist_down = min(dist_down, other_car.pos.y - car.pos.y) if other_car.pos.y >= car.pos.y \
                            else dist_down
                    elif overlap(other_car.pos, other_car.w, other_car.h,
                                 Point(car.pos.x, car.pos.y - BLOCK_SIZE), car.w, car.h):
                        dist_up = min(dist_up, car.pos.y - other_car.pos.y) if car.pos.y >= other_car.pos.y else dist_up
                else:
                    if other_car.pos.x == car.pos.x:
                        dist_front = min(dist_front, other_car.pos.y - car.pos.y) if other_car.pos.y >= car.pos.x \
                            else dist_front
                    elif overlap(other_car.pos, other_car.w, other_car.h,
                                 Point(car.pos.x + BLOCK_SIZE, car.pos.y), car.w, car.h):
                        dist_down = min(dist_down, other_car.pos.x - car.pos.x) if other_car.pos.x >= car.pos.x \
                            else dist_down
                    elif overlap(other_car.pos, other_car.w, other_car.h,
                                 Point(car.pos.x - BLOCK_SIZE, car.pos.y), car.w, car.h):
                        dist_up = min(dist_up, car.pos.x - other_car.pos.x) if car.pos.x >= other_car.pos.x else dist_up

        state = [
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            isinstance(car.res, CrossingSegment),
            dist_front,
            dist_down,
            dist_up,

            # Food location
            self.goals[player].pos.x - car.pos.x,  # food left
            self.goals[player].pos.y - car.pos.y,  # food up
        ]

        return np.array(state, dtype=int)
