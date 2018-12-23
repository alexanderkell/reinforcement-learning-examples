from multiagent.core import Agent
"""
File name: agent
Date created: 22/12/2018
Feature: #Enter feature description here
"""

__author__ = "Alexander Kell"
__copyright__ = "Copyright 2018, Alexander Kell"
__license__ = "MIT"
__email__ = "alexander@kell.es"


class Agent(Agent):

    def __init__(self):

        super().__init__()
        self.plants = []

        self.money = 50000

        self.discount_rate = 0.05

