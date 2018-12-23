import sys
sys.path.insert(0, '/Users/b1017579/Documents/PhD/Projects/10. ELECSIM')

from src.plants.plant_costs.estimate_costs.estimate_costs import select_cost_estimator
from src.plants.plant_registry import PlantRegistry
import numpy as np
from multiagent.core import World
from multiagent.scenario import BaseScenario
from multiagent.scenarios.electricty_market.agent import Agent
from random import choice, randint

class Scenario(BaseScenario):
    def make_world(self):
        world = World()
        # add agents
        world.agents = [Agent() for i in range(10)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.collide = False
            agent.silent = True
            agent.adversary = False
            agent.movable = False
            agent.silent = False
            agent.blind = False
            agent.u_range = 5000
        # make initial conditions
        self.reset_world(world)
        return world

    def reset_world(self, world):
        # random properties for agents
        plant_types = ['Nuclear','Coal','Gas','PV','Offshore']
        for i, agent in enumerate(world.agents):
            agent.plants = [self.create_power_plant(2000, choice(plant_types), randint(20,1500))]*5
            agent.money = 0

    def reward(self, agent, world):
        reward = agent.money
        return reward

    def observation(self, agent):
        # observations whether bids have been accepted or rejected

        # bid_result = [x.status for x in agent.bids]
        result = agent.bid.result
        return result

        # get positions of all entities in this agent's reference frame
        # entity_pos = []
        # for entity in world.landmarks:
        #     entity_pos.append(entity.state.p_pos - agent.state.p_pos)
        # return np.concatenate([agent.state.p_vel] + entity_pos)

    def create_power_plant(self, start_year, plant_type, capacity):
        estimated_cost_parameters = select_cost_estimator(start_year=start_year,
                                                          plant_type=plant_type,
                                                          capacity=capacity)
        power_plant_obj = PlantRegistry(plant_type).plant_type_to_plant_object()
        power_plant = power_plant_obj(name="test", plant_type=plant_type,
                                      capacity_mw=capacity, construction_year=start_year,
                                      **estimated_cost_parameters)
        return power_plant
