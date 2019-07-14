import gym
from gym import error, spaces, utils
from gym.utils import seeding

from gym.spaces import Tuple, Box
import numpy as np
import ray
from ray import tune
from ray.tune import register_env, grid_search
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.tune import register_env, grid_search
import collections
from ray.tune.logger import pretty_print

from ray.rllib.agents.dqn.dqn import DQNTrainer
from ray.rllib.agents.dqn.dqn_policy import DQNTFPolicy
from ray.rllib.agents.ppo.ppo import PPOTrainer
from ray.rllib.agents.ppo.ppo_policy import PPOTFPolicy
from ray.rllib.tests.test_multi_agent_env import MultiCartpole


import ray
import ray.rllib.agents.ppo as ppo



class FooEnv(MultiAgentEnv):

    def __init__(self, number_of_agents=10):
        self.number_of_agents = number_of_agents

        self.action_space = spaces.Box(low=-1, high=1000, shape=(1,), dtype=np.float)
        self.observation_space = spaces.Box(low=-1, high=1000, shape=(1,), dtype=np.float)
        print("Initting FooEnv")
        self.total_capacity_required = 50
        self.number_of_steps = 0

    def step(self, action_dict):
        self.number_of_steps += 1
        reward_dict = dict.fromkeys(action_dict)
        sorted_x = sorted(action_dict.items(), key=lambda kv: kv[1])
        sorted_dict = collections.OrderedDict(sorted_x)
        obs = {}
        total_capacity_required = 50
        for key, action in sorted_dict.items():
            total_capacity_required -= 10

            if total_capacity_required > 0:
                reward_dict[key] = action[0]
                obs[key] = [action[0]]
            else:
                reward_dict[key] = np.array(0)
                obs[key] = [np.array(0)]
# 
        if self.number_of_steps < 50:
            dones = {"__all__": False}
        else:
            dones = {"__all__": True}
        infos = {}
        # print("reward_dict: {}".format(reward_dict))
        return obs, reward_dict, dones, infos
             
    def reset(self):
        self.total_capacity_required = 50

        # return {"agent_1": np.array(0).reshape(1,), "agent_2": np.array(0).reshape(1,)}
        return {i: [np.array(0)] for i, _ in enumerate(range(self.number_of_agents))}


if __name__ == "__main__":

    def policy_mapping_fn(agent_id):
        # print("agent_id is: {}".format(agent_id))
        # return "agent_1"
        if agent_id < 7:
            return "agent_1"
        else:
            return "agent_2"

        # if agent_id < 2:
        #     return "agent_1"
        # elif agent_id < 4:
        #     return "agent_2"
        # elif agent_id < 6:
        #     return "agent_3"
        # elif agent_id < 8:
        #     return "agent_4"
        # elif agent_id < 10:
        #     return "agent_5"

    ray.init()
    obs_space = FooEnv().observation_space
    action_space = FooEnv().action_space

    register_env("market23_env", lambda _: FooEnv())

    policies = {
        "agent_1": (PPOTFPolicy, obs_space, action_space, {}),
        "agent_2": (PPOTFPolicy, obs_space, action_space, {}),
        "agent_3": (PPOTFPolicy, obs_space, action_space, {}),
        "agent_4": (PPOTFPolicy, obs_space, action_space, {}),
        "agent_5": (PPOTFPolicy, obs_space, action_space, {}),
    }

    tune.run(
        "PPO",
        stop={
            "timesteps_total": 1000000,
        },
        config={
            "env": "market23_env",  # or "corridor" if registered above
            # "lr": grid_search([1e-2, 1e-4, 1e-6]),  # try different lrs
            "lr": grid_search([1e-4]),  # try different lrs
            "num_workers": 3,  # parallelism
            "env_config": {
                    "number_of_agents": 20,
                },
            "timesteps_per_iteration": 1000,
            "min_iter_time_s": 3,
            # "buffer_size": 1000,
            # "learning_starts": 1000,
            # "train_batch_size": 128,
            # "sample_batch_size": 32,
            # "target_network_update_freq": 500,
            "multiagent": {
                "policies": {
                    # the first tuple value is None -> uses default policy
                    "agent_1": (None, obs_space, action_space, {}),
                    "agent_2": (None, obs_space, action_space, {})
                },
                "policy_mapping_fn":
                    tune.function(lambda agent_id: "agent_1" if agent_id < 7 else "agent_2"),
            }
        }
    )

    # ppo_trainer = PPOTrainer(
    #     env="market23_env",
    #     config={
    #         "multiagent": {
    #             "policies": policies,
    #             "policy_mapping_fn": policy_mapping_fn,
    #             "policies_to_train": ["agent_1", "agent_2"],
    #         },
    #         # disable filters, otherwise we would need to synchronize those
    #         # as well to the DQN agent
    #         # "observation_filter": "NoFilter",
    #     })

    # for i in range(100):
    #     print(pretty_print(ppo_trainer.train()))

    # config = {
    #     "num_gpus": 0,
    #     "num_workers": 2,
    #     "optimizer": {
    #         "num_replay_buffer_shards": 1,
    #     },
    #     "min_iter_time_s": 3,
    #     "buffer_size": 1000,
    #     "learning_starts": 1000,
    #     "train_batch_size": 128,
    #     "sample_batch_size": 32,
    #     "target_network_update_freq": 500,
    #     "timesteps_per_iteration": 1000,
    # }

    




    # trainer = ppo.PPOAgent(env="market23_env")
    # while True:
    #     print("training")
    #     print(trainer.train())





    # group = True

    # ray.init()
    # tune.run(
    #     "PPO",
    #     stop={
    #         "timesteps_total": 200000,
    #     },
    #     config=dict(config, **{
    #         "env": "market23_env",
    #     }),
    # )