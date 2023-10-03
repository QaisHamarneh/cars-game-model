import math
import os
import random
from collections import deque

import torch

from constants import *
from learning_agent.nn import LinearQNet, QTrainer


class CarAgent:
    def __init__(self, game, player, eval=False, file_name="model", uniform=False):
        self.game = game
        self.n_actions = game.n_actions
        self.player = player
        self.file_name = file_name
        self.record = 0
        self.rewards = 0
        if not uniform:
            self.file_name = f"{self.file_name}_{self.player}.pth"
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.99  # discount rate
        self.state_size = len(game.get_state(player))
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = LinearQNet(
            self.player, self.state_size, 256, self.n_actions)

        if eval:
            self.load_model()
        else:
            self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def load_model(self):
        model_folder_path = '../models'
        fn = os.path.join(model_folder_path, self.file_name)
        self.model.load_state_dict(torch.load(fn))

    def remember(self, state, action, reward, next_state, done):
        # popleft if MAX_MEMORY is reached
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(
                self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state, eval=False, rand=False):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * self.n_games / EPS_DECAY)
        final_move = [0] * self.n_actions
        if rand or (not eval and random.random() < self.epsilon):
            move = random.randint(0, self.n_actions - 1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def train(self):
        # get old state
        state_old = self.game.get_state(self.player)

        # get move
        final_move = self.get_action(state_old)

        # perform move and get new state
        reward, gameover, score = self.game.play_step(self.player, final_move)
        state_new = self.game.get_state(self.player)

        self.rewards += reward
        # train short memory
        self.train_short_memory(
            state_old, final_move, reward, state_new, gameover)

        # remember
        self.remember(
            state_old, final_move, reward, state_new, gameover)

        if gameover:
            # train long memory, plot result
            self.n_games += 1
            self.train_long_memory()
            print(f"Game {self.n_games}: player {self.player} score {score}")

            if score > self.record:
                self.record = score
                print(f"Game {self.n_games}: player {self.player} record {self.record}")
                self.model.save(file_name=self.file_name)
            self.rewards = 0

        return gameover

    def eval(self, rand=False):
        # get old state
        state_old = self.game.get_state(self.player)

        # get move
        final_move = self.get_action(state_old, eval=True, rand=rand)

        # perform move and get new state
        _, gameover, score = self.game.play_step(self.player, final_move)

        return gameover, score
