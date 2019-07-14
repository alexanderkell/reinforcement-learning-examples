"""
File name: market_env
Date created: 21/12/2018
Feature: #Enter feature description here
"""

__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"

import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np


class MarketEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    """
    Description:
        A market is created where an agent must maximise revenue from selling electricity. In this simple case,
        a bid is accepted as long as the bid submitted is smaller than 50. Therefore, the agent should learn to
        always bid 49.99
    Observation:
        Type: Discrete(4)
        Num	Observation                 0         1
        0	Bid status                  rejected  accepted
    Actions:
        Type: Box()
        Num	Range
        0	-inf, inf   Bid made to sell electricty
        Note: The amount the velocity is reduced or increased is not fixed as it depends on the angle the pole is pointing. This is because the center of gravity of the pole increases the amount of energy needed to move the cart underneath it
    Reward:
        Reward is 0.1 for every unit of money earned
    Starting State:
        All observations are assigned 0
    Episode Termination:
        Episode length is greater than 200
    Solved Requirements
        Considered solved when the average reward is greater than or equal to 9800.
    """
    def __init__(self):

        self.action_space = spaces.Box(low=-1000, high=1000, shape=(1,), dtype=np.float32)
        self.observation_space = np.array([0])

        self.number_of_steps = 0

    def step(self, action):
        done = False
        reward = 0
        print("action: {}".format(action))
        if action > 50 or action < 0.4:
            bid_status = 0
            reward = -10
        else:
            bid_status = 1
            reward = int(1000*np.round(action,3))
        self.number_of_steps += 1
        if self.number_of_steps > 200:
            done = True

        # bid_status = spaces.Discrete(bid_status)
        #  the next state, the reward for the current state, done, additional info on our problem
        return np.array([bid_status]), reward, done, {}

    def reset(self):
        self.number_of_steps = 0

        return np.array([0])

    def render(self, mode='human', close=False):
        # print("num steps {}".format(self.number_of_steps))
        # print("action")

        return False
