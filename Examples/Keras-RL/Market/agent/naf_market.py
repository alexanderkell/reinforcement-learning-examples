import numpy as np
import gym

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, Concatenate
from keras.optimizers import Adam

from keras.backend import clear_session

from rl.agents import NAFAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess
from rl.core import Processor

from gym_market.gym_market.envs.market_env import SharedEnv, MarketEnv

from multiprocessing.dummy import Pool as ThreadPool

import gym_market.gym_market.envs.market_env

"""
File name: naf_market
Date created: 22/12/2018
Feature: # Agent which implements NAF reinforcement algorithm for market_evn
"""

__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"


class MarketProcessor(Processor):
    def process_reward(self, reward):
        # The magnitude of the reward can be important. Since each step yields a relatively
        # high reward, we reduce the magnitude by two orders.
        return reward / 100.


ENV_NAME = 'MarketEnv-v0'
#
#
# Get the environment and extract the number of actions.
# env = gym.make(ENV_NAME)
# np.random.seed(123)
# env.seed(123)
# assert len(env.action_space.shape) == 1
# nb_actions = env.action_space.shape[0]
# # env.observation_space.shape

# nb_actions = 1
# env.observation_space.shape = (1,)

# Build all necessary models: V, mu, and L networks.
V_model = Sequential()
V_model.add(Flatten(input_shape=(1,) + (1,)))
V_model.add(Dense(16))
V_model.add(Activation('relu'))
V_model.add(Dense(16))
V_model.add(Activation('relu'))
V_model.add(Dense(16))
V_model.add(Activation('relu'))
V_model.add(Dense(1))
V_model.add(Activation('linear'))
print(V_model.summary())


mu_model = Sequential()
mu_model.add(Flatten(input_shape=(1,) + (1,)))
mu_model.add(Dense(16))
mu_model.add(Activation('relu'))
mu_model.add(Dense(16))
mu_model.add(Activation('relu'))
mu_model.add(Dense(16))
mu_model.add(Activation('relu'))
mu_model.add(Dense(1))
mu_model.add(Activation('linear'))
print(mu_model.summary())


action_input = Input(shape=(1,), name='action_input')
observation_input = Input(shape=(1,) + (1,), name='observation_input')
x = Concatenate()([action_input, Flatten()(observation_input)])
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(32)(x)
x = Activation('relu')(x)
x = Dense(((1 * 1 + 1) // 2))(x)
x = Activation('linear')(x)
L_model = Model(inputs=[action_input, observation_input], outputs=x)
print(L_model.summary())


# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
processor = MarketProcessor()
memory = SequentialMemory(limit=100000, window_length=1)
random_process = OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=.3, size=1)

shared = SharedEnv()


def fit_model(agent_idx):
# for agent_idx in range(3):
    print(agent_idx)
    env = MarketEnv(shared=shared, idx=agent_idx)
    agent = NAFAgent(nb_actions=1, V_model=V_model, L_model=L_model, mu_model=mu_model,
                     memory=memory, nb_steps_warmup=100, random_process=random_process,
                     gamma=.99, target_model_update=1e-3, processor=processor)

    agent.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])

    # Okay, now it's time to learn something! We visualize the training here for show, but this
    # slows down training quite a lot. You can always safely abort the training prematurely using
    # Ctrl + C.
    agent.fit(env, nb_steps=50000, visualize=True, verbose=2, nb_max_episode_steps=200)

    # After training is done, we save the final weights.
    agent.save_weights('cdqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)

    # Finally, evaluate our algorithm for 5 episodes.
    agent.test(env, nb_episodes=10, visualize=True, nb_max_episode_steps=200)

pool = ThreadPool(3)
results = pool.map(fit_model, [1, 2, 3])
