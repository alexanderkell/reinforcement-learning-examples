from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
"""Example of running a policy server. Copy this file for your use case.
To try this out, in two separate shells run:
    $ python cartpole_server.py
    $ python cartpole_client.py
"""

import os
from gym import spaces
from gym.spaces import Tuple, Box
import numpy as np

import ray
# from ray.rllib.agents.dqn import DQNTrainer
from ray.rllib.agents.pg import PGTrainer
# from ray.rllib.env.external_env import ExternalEnv
from ray.rllib.env.external_multi_agent_env import ExternalMultiAgentEnv
from ray.rllib.utils.policy_server import PolicyServer
from ray.tune.logger import pretty_print
from ray.tune.registry import register_env
from ray import tune
from ray.rllib.env.multi_agent_env import MultiAgentEnv
import collections

import sys
sys.path.append("/Users/b1017579/Documents/PhD/Projects/12-Reinforcement-Learning/Examples/")

from custom_gym.gym_foo.gym_foo.envs.foo_env import FooEnv

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9900
CHECKPOINT_FILE = "last_checkpoint.out"

class MarketServing(ExternalMultiAgentEnv):
    
    def __init__(self):
        ExternalMultiAgentEnv.__init__(
            self, FooEnv.action_space,
            FooEnv.observation_space)

    def run(self):
        print("Starting policy server at {}:{}".format(SERVER_ADDRESS,
                                                       SERVER_PORT))
        server = PolicyServer(self, SERVER_ADDRESS, SERVER_PORT)
        server.serve_forever()


if __name__ == "__main__":

    grouping = {
        "group_1":
            ['agent_1', "agent_2", 'agent_3', 'agent_4', 'agent_5', 'agent_6', 'agent_7', 'agent_8', 'agent_9', 'agent_10'],
    }

    obs_space_1 = Tuple([FooEnv.observation_space]*10)
    action_space_1 = Tuple([FooEnv.action_space]*10)
    obs_space_2 = Tuple([FooEnv.observation_space]*2)
    action_space_2 = Tuple([FooEnv.action_space]*2)

    ray.init()
    register_env("srv", lambda _: MarketServing())

    # We use DQN since it supports off-policy actions, but you can choose and
    # configure any agent.
    dqn = PGTrainer(
        env="srv",
        config={
            # Use a single process to avoid needing to set up a load balancer
            "num_workers": 0,
            # # # Configure the agent to run short iterations for debugging
            # # "exploration_fraction": 0.01,
            # # "learning_starts": 100,
            # # "timesteps_per_iteration": 200,
            # "multiagent": {
            #     "grouping":
            #         grouping,
            #     "policies": {
            #         # the first tuple value is None -> uses default policy
            #         "function_1": (None, obs_space_1, action_space_1, {}),
            #         "function_2": (None, obs_space_2, action_space_2, {})
            #     },
            #     "policy_mapping_fn":
            #         # tune.function(lambda agent_id: "agent_{}".format(agent_id+1)),
            #         tune.function(lambda agent_id: "function_1" if agent_id == "group_1" else "function_2"),
            # },
        })

    # # Attempt to restore from checkpoint if possible.
    # if os.path.exists(CHECKPOINT_FILE):
    #     checkpoint_path = open(CHECKPOINT_FILE).read()
    #     print("Restoring from checkpoint path", checkpoint_path)
    #     dqn.restore(checkpoint_path)

    # Serving and training loop
    while True:
        print(pretty_print(dqn.train()))
        checkpoint_path = dqn.save()
        print("Last checkpoint", checkpoint_path)
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(checkpoint_path)