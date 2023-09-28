import random
from collections import namedtuple
import numpy as np
import pygame

from cars_gui import CarGui
from direction import Direction


Point = namedtuple('Point', 'x, y')


def dist(p1, p2):
    return np.linalg.norm([p1.x - p2.x, p1.y - p2.y])


class CarsGame:

    def __init__(self, players=2, render=False):
        self.players = players
        self.n_actions = 3
        self.render = render
        self.size = self.players * 10
        # init display
        self.gui = None
        if self.render:
            self.gui = CarGui(self.players, size=self.size)
        self.reset()

    def reset(self):
        # init game state
        self.directions = [Direction.LEFT if i % 2 ==
                           0 else Direction.RIGHT for i in range(self.players)]

        self.cars = [Point(self.size // 2, i * self.size // (self.players + 1))
                      for i in range(1, self.players + 1)]

        self.scores = [0] * self.players
        self.foods = [None] * self.players
        self.got_food = [False] * self.players
        self.useless_iterations = 0
        for i in range(self.players):
            self._place_food(i)

    def activate_gui(self):
        if self.gui is None:
            self.gui = CarGui(self.players, size=self.size)
        self.render = True

    def _place_food(self, player):
        self.got_food[player] = True
        if all(self.got_food):
            self.useless_iterations = 0
            self.got_food = [False] * self.players

        x = random.randint(0, self.size -1)
        y = random.randint(0, self.size -1)
        while any([Point(x, y) == self.cars[i] for i in range(self.players)]):
            x = random.randint(0, self.size -1)
            y = random.randint(0, self.size -1)

        self.foods[player] = Point(x, y)

    def play_step(self, player, action):
        self.useless_iterations += 1

        # 2. move
        old_dist_to_food = dist(self.cars[player], self.foods[player])
        self._move(player, action)  # update the head

        new_dist_to_food = dist(self.cars[player], self.foods[player])

        # 3. check if game over
        reward = 0
        # if self.useless_iterations > 4 * self.size:
        #     reward -= 1

        if new_dist_to_food >= old_dist_to_food:
            reward -= 1
        else:
            reward += 1
        game_over = False
        if self.is_collision(player) or self.useless_iterations > self.size**2:
            game_over = True
            reward = -10
            return reward, game_over, self.scores[player]

        # 4. place new food or just move
        if self.cars[player] == self.foods[player]:
            self.scores[player] += 1
            reward = 10
            self._place_food(player)

        # 5. update ui and clock
        if self.render and player == self.players - 1:
            self.gui._update_ui(self.cars, self.directions, self.foods, self.scores)
            self.gui.tick()
        # 6. return game over and score
        return reward, game_over, self.scores[player]

    def is_collision(self, player, pt=None):
        if pt is None:
            pt = self.cars[player]
        # hits boundary
        if pt.x > self.size - 1 or pt.x < 0 or pt.y > self.size - 1 or pt.y < 0:
            return True
        # hits itself
        if any([pt == self.cars[i] for i in range(self.players) if i != player]):
            return True
        return False

    def _move(self, player, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN,
                      Direction.LEFT, Direction.UP]

        idx = clock_wise.index(self.directions[player])

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        x = self.cars[player].x
        y = self.cars[player].y
        if new_dir == Direction.RIGHT:
            x += 1
        elif new_dir == Direction.LEFT:
            x -= 1
        elif new_dir == Direction.DOWN:
            y += 1
        elif new_dir == Direction.UP:
            y -= 1

        self.directions[player] = new_dir
        self.cars[player] = Point(x, y)


    def get_state(self, player):
        car = self.cars[player]
        point_l = Point(car.x - 1, car.y)
        point_r = Point(car.x + 1, car.y)
        point_u = Point(car.x, car.y - 1)
        point_d = Point(car.x, car.y + 1)

        # point_ll = Point(car.x - 2, car.y)
        # point_rr = Point(car.x + 2, car.y)
        # point_uu = Point(car.x, car.y - 2)
        # point_dd = Point(car.x, car.y + 2)

        dir_l = self.directions[player] == Direction.LEFT
        dir_r = self.directions[player] == Direction.RIGHT
        dir_u = self.directions[player] == Direction.UP
        dir_d = self.directions[player] == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and self.is_collision(player, point_r)) or
            (dir_l and self.is_collision(player, point_l)) or
            (dir_u and self.is_collision(player, point_u)) or
            (dir_d and self.is_collision(player, point_d)),

            # (dir_r and self.is_collision(player, point_rr)) or
            # (dir_l and self.is_collision(player, point_ll)) or
            # (dir_u and self.is_collision(player, point_uu)) or
            # (dir_d and self.is_collision(player, point_dd)),

            # Danger right
            (dir_u and self.is_collision(player, point_r)) or
            (dir_d and self.is_collision(player, point_l)) or
            (dir_l and self.is_collision(player, point_u)) or
            (dir_r and self.is_collision(player, point_d)),

            # (dir_u and self.is_collision(player, point_rr)) or
            # (dir_d and self.is_collision(player, point_ll)) or
            # (dir_l and self.is_collision(player, point_uu)) or
            # (dir_r and self.is_collision(player, point_dd)),

            # Danger left
            (dir_d and self.is_collision(player, point_r)) or
            (dir_u and self.is_collision(player, point_l)) or
            (dir_r and self.is_collision(player, point_u)) or
            (dir_l and self.is_collision(player, point_d)),

            # (dir_d and self.is_collision(player, point_rr)) or
            # (dir_u and self.is_collision(player, point_ll)) or
            # (dir_r and self.is_collision(player, point_uu)) or
            # (dir_l and self.is_collision(player, point_dd)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            self.foods[player].x < car.x,  # food left
            self.foods[player].x > car.x,  # food right
            self.foods[player].y < car.y,  # food up
            self.foods[player].y > car.y  # food down
        ]

        return np.array(state, dtype=int)


if __name__ == '__main__':
    players = 4
    game = CarsGame(render=True, players=players)
    scores = [0] * players
    episodes = 10
    for epi in range(episodes):
        game_over = False
        game.reset()
        # game loop
        while True:
            for player in range(players):
                action = [0, 0, 0]
                ran = random.choice(range(3))
                action[ran] = 1
                _, p_game_over, scores[player] = game.play_step(player, action)
                game_over = game_over or p_game_over
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            if game_over:
                break

        print(f"Episode {epi}:")

        print(
            [f"Score {player}: {scores[player]}" for player in range(players)])

    pygame.quit()
