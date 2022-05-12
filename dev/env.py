from xmlrpc.client import Boolean
from gym import Env
from gym.spaces import Discrete, Box, Dict, MultiBinary
import numpy as np
import pandas as pd


class SchedulingEnv(Env):
    """A personnel scheduling environment for OpenAI gym"""

    def __init__(self, pool, schedule):
        schedule = pd.get_dummies(schedule,drop_first=True)
        self.shift_features = schedule.shape[1]
        for i in pd.get_dummies(pool).columns.to_list():
            schedule[i] = 0
        
        self.schedule = schedule
        self.state = self.schedule.to_numpy()
        self.count_workers = len(pool)
        self.count_shifts = len(schedule)
        self.shift_number = 0
        
        ## SPACES
        # action space: Employees we can assign to shifts
        self.action_space = Discrete(self.count_workers)

 
    def step(self, action):
        
        # assign worker
        self.state[self.shift_number,(self.shift_features+action)] = 1


        # done
        filled_check = self.state[:,self.shift_features:].sum() 
        if filled_check < self.count_shifts:
            done = False
            self.shift_number += 1
        else:
            done = True
        
        # reward  
        if done == False:
             reward = 0
        
        else:
            assignment_reward = self.count_shifts
            # check if an employee worked twice on the same day 
            # if so, b2b shift penalty should be applied
            b2b_penalty = 0
            b2b_penalty += 1 if self.state[:,self.shift_features][0:2].sum() == 0 or \
                                self.state[:,self.shift_features][0:2].sum() > 1 else 0
            b2b_penalty += 1 if self.state[:,self.shift_features][2:4].sum() == 0 or \
                                self.state[:,self.shift_features][2:4].sum() > 1  else 0
            reward = assignment_reward - (b2b_penalty) 

        # info placeholder
        info = {}

        return self.state, reward, done, info
 
    def render(self):
        # graph viz?
        pass
    
    def reset(self):
        self.shift_number = 0
        self.state = self.schedule.to_numpy()
        return self.state
