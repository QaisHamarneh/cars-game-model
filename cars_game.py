import random
from collections import namedtuple
import numpy as np
import pygame

from cars_gui import CarGui
from helper_classes import Car, Goal, Road, Direction, Point, create_random_car, overlap, dir_axis
from constants import *

def dist(p1, p2):
    return np.linalg.norm([p1.x - p2.x, p1.y - p2.y])


class CarsGame:

    def __init__(self, roads:list[Road], players, cars = None, render=False):
        self.roads = roads
        self.players = players
        self.cars = cars
        if self.cars is None:
            self.cars = []
            for _ in range(self.players):
                self.cars.append(create_random_car(self.roads, self.cars))
        self.n_actions = 5
        self.render = render
        # init display
        self.gui = None
        if self.render:
            self.gui = CarGui(roads=self.roads)
        self.reset()

    def reset(self):
        # init game state
        self.scores = [0] * self.players
        self.foods = [None] * self.players
        self.useless_iterations = [0] * self.players
        self.cars = []
        for i in range(self.players):
            self.cars.append(create_random_car(self.roads, self.cars))
        for i in range(self.players):
            self._place_food(i)

    def activate_gui(self):
        if self.gui is None:
            self.gui = CarGui(roads=self.roads)
        self.render = True

    def _place_food(self, player):
        self.useless_iterations[player] = 0

        road = random.choice(self.roads)
        lane = random.choice(road.left_lanes + road.right_lanes)
        x = random.randint(BLOCK_SIZE, WINDOW_SIZE -BLOCK_SIZE)
        p = Point(x, lane.top) if lane.road.horizontal \
            else Point(lane.top, x)
        while any([overlap(p, BLOCK_SIZE, BLOCK_SIZE, 
                           self.cars[i].pos, self.cars[i].w, self.cars[i].h) 
                   for i in range(self.players)]):
            x = random.randint(BLOCK_SIZE, WINDOW_SIZE -BLOCK_SIZE)
            p = Point(x, lane.top) if lane.road.horizontal \
                else Point(lane.top, x)

        self.foods[player] = Goal(lane, x, self.cars[player])

    def play_step(self, player, action):
        self.useless_iterations[player] += 1
        car = self.cars[player]
        reward = 0
        game_over = False
        
        # 1.a. Someone else hit this car
        # if self.is_collision(player):
        #     game_over = True
        #     reward = 0
        #     car.dead = True
        #     return reward, game_over, self.scores[player]
        
        # 1.b. Illegal turn
        action_ind = action.index(1)

        # 2. move
        old_dist_to_food = dist(car.pos, self.foods[player].pos)
        moved = self._move(player, action_ind)  # update the head

        new_dist_to_food = dist(car.pos, self.foods[player].pos)

        # 3. check reward
        if self.is_collision(player) or self.is_illegal(car) or self.useless_iterations[player] > WINDOW_SIZE * 2:
            game_over = True
            reward = -100
            car.dead = True
            return reward, game_over, self.scores[player]

        if new_dist_to_food <= old_dist_to_food:
            reward += 5

        if not moved:
            reward -= 5

        # 4. place new food or just move
        if overlap(self.cars[player].pos, self.cars[player].w, self.cars[player].h, 
                   self.foods[player].pos, BLOCK_SIZE, BLOCK_SIZE):
            self.scores[player] += 1
            reward = 1000
            self._place_food(player)

        # 5. update ui and clock
        if self.render and player == self.players - 1:
            self.gui._update_ui(self.cars, self.foods, self.scores)
            self.gui.tick()
        # 6. return game over and score
        return reward, game_over, self.scores[player]

    def is_collision(self, player, pt=None):
        car = self.cars[player]
        if pt is None:
            pt = self.cars[player].pos
        if car.road.horizontal:
            front = pt.x + dir_axis[car.dir][0] * car.w
        else:
            front = pt.y + dir_axis[car.dir][1] * car.h
        # hits boundary
        if front > WINDOW_SIZE - 1 or front.x < 0 or front > WINDOW_SIZE - 1 or front.y < 0:
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

    def in_intersection(self, car):
        if car.road.horizontal:
            front = car.pos.x + dir_axis[car.dir][0] * car.w
        else:
            front = car.pos.y + dir_axis[car.dir][1] * car.h
        if any([road.top <= front <= road.bottom 
                for road in self.roads 
                if road.horizontal != car.road.horizontal
            ]) or front <= BLOCK_SIZE or front >= WINDOW_SIZE - BLOCK_SIZE:
            return True
        return False
    
    def is_illegal(self, car):
        if car.dir != car.lane.dir and not self.in_intersection(car):
            return True
        if car.lane.num < 0 or car.lane.num >= len(car.lanes):
            return True
        return False

    def _move(self, player, action_ind):
        # [straight, right, left]
        car = self.cars[player]

        clock_wise = [Direction.RIGHT, Direction.DOWN,
                      Direction.LEFT, Direction.UP]

        idx = clock_wise.index(car.dir)
        change_workd = True
        match action_ind:
            case 0:
                new_dir = clock_wise[idx]  # no change
            case 1:
                new_dir = clock_wise[idx]  # no change
                change_workd = car.change_lane(1)
            case 2:
                new_dir = clock_wise[idx]  # no change
                change_workd = car.change_lane(-1)
            case 3:
                new_dir = clock_wise[idx]  
                car.speed -= 1              # slow down
            case 4:
                new_dir = clock_wise[idx]  
                car.speed += 1              # speed up
            case 5:
                next_idx = (idx + 1) % 4
                new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
            case 6:
                next_idx = (idx - 1) % 4
                new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        if action_ind < 5:
            match new_dir:
                case Direction.RIGHT:
                    car.move(car.speed, 0)
                case Direction.LEFT:
                    car.move(- car.speed, 0)
                case Direction.DOWN:
                    car.move(0, car.speed)
                case Direction.UP:
                    car.move(0, - car.speed)
        elif action_ind == 3 and self.in_intersection(car):
            return car.turn(self.roads, new_dir)
        
        return change_workd
            


    def get_state(self, player):
        car = self.cars[player]

        point_l = Point(car.pos.x - car.speed, car.pos.y)
        point_r = Point(car.pos.x + car.speed, car.pos.y)
        point_u = Point(car.pos.x, car.pos.y - car.speed)
        point_d = Point(car.pos.x, car.pos.y + car.speed)

        left_lane_free = False
        if car.lane.num > 0:
            left_lane_free = self.is_collision(player, Point(car.pos.x, car.lanes[car.lane.num - 1].top)) 

        right_lane_free = False
        if car.lane.num < len(car.lanes) - 1:
            right_lane_free = self.is_collision(player, Point(car.pos.x, car.lanes[car.lane.num + 1].top))
        
        upper_lane_free = False
        if car.lane.num > 0:
            upper_lane_free = self.is_collision(player, Point(car.lanes[car.lane.num - 1].top, car.pos.y))
        
        lower_lane_free = False
        if car.lane.num < len(car.lanes) - 1:
            lower_lane_free = self.is_collision(player, Point(car.lanes[car.lane.num + 1].top, car.pos.y))

        dir_l = car.dir == Direction.LEFT
        dir_r = car.dir == Direction.RIGHT
        dir_u = car.dir == Direction.UP
        dir_d = car.dir == Direction.DOWN

        state = [
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Danger straight
            (dir_r and self.is_collision(player, point_r)) or
            (dir_l and self.is_collision(player, point_l)) or
            (dir_u and self.is_collision(player, point_u)) or
            (dir_d and self.is_collision(player, point_d)),

            # # Danger right
            # (dir_u and self.is_collision(player, point_r)) or
            # (dir_d and self.is_collision(player, point_l)) or
            # (dir_l and self.is_collision(player, point_u)) or
            # (dir_r and self.is_collision(player, point_d)),

            # # Danger left
            # (dir_d and self.is_collision(player, point_r)) or
            # (dir_u and self.is_collision(player, point_l)) or
            # (dir_r and self.is_collision(player, point_u)) or
            # (dir_l and self.is_collision(player, point_d)),

            # Can change lane -1
            car.lane.num > 0 and
            ((dir_r or dir_l) and left_lane_free) or
            ((dir_d or dir_u) and upper_lane_free),

            # Can change lane +1
            car.lane.num < len(car.lanes) - 1 and
            ((dir_r or dir_l) and right_lane_free) or
            ((dir_d or dir_u) and lower_lane_free),

            # Can turn
            self.in_intersection(car),

            # Food location
            self.foods[player].pos.x < car.pos.x,  # food left
            self.foods[player].pos.x > car.pos.x,  # food right
            self.foods[player].pos.y < car.pos.y,  # food up
            self.foods[player].pos.y > car.pos.y  # food down
        ]

        return np.array(state, dtype=int)

