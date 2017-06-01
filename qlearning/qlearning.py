#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import util as utl
import pandas as pd
import numpy as np
import math
import talib

DEBUG=True


class Environment:
    def __init__(self):
        self.data = pd.read_csv("/home/unicorn/work/datasets/rates_2017_january_may_1min.csv")
        self.state_idx = 0
        self.long_positions = False
        self.close_prices = self.data['close'].values

        self.upper_band_5, \
        self.sma_5, \
        self.lower_band_5 = talib.BBANDS(
            self.close_prices,
            timeperiod=5,
            # number of non-biased standard deviations from the mean
            nbdevup=2,
            nbdevdn=2,
            # Moving average type: simple moving average here
            matype=0)

        self.returns = np.zeros(len(self.data))
        self.returns[1:] = (self.close_prices[1:] / self.close_prices[:-1])-1


    def reset(self):
        self.state_idx = 0
        self.long_positions = 0


    def step(self, action):
        self.state_idx = self.state_idx + 1

        observation = None
        reward = 0
        done = self.state_idx >= len(self.data)
        info = None

        if not done:
            if action == "BUY" and not self.long_positions:
                self.long_positions = True
            elif action == "SELL" and self.long_positions:
                self.long_positions = False

            if self.long_positions:
                reward = self.returns[self.state_idx]

            observation = self.__compute_state()
            
        return observation, reward, done, info



    def __compute_state(self):
        if math.isnan(self.upper_band_5[self.state_idx]) \
           or math.isnan(self.lower_band_5[self.state_idx]):
            return 3 if self.long_positions else 2

        isAbove = self.close_prices[self.state_idx] > self.upper_band_5[self.state_idx]
        isBelow = self.close_prices[self.state_idx] < self.lower_band_5[self.state_idx]
        isBetween = \
                    self.close_prices[self.state_idx] <= self.upper_band_5[self.state_idx] \
                    and self.close_prices[self.state_idx] >= self.lower_band_5[self.state_idx]

        if isBetween:
            return 3 if self.long_positions else 2
        if isBelow:
            return 1 if self.long_positions else 0
        if isAbove:
            return 5 if self.long_positions else 4

    
def log(message):
    if DEBUG:
        print message

def test_run():

    log("Init Q w/ random values")
    Q = np.random.normal(size=(6,3))  ## 3 actions * 6 states (just to try, there will be much more")
    log("Q matrix = {}".format(Q))

    learning_rate = 0.3
    discount_rate = 0.3
  


    env = Environment()
    env.reset()

    observation, reward, done, info = env.step("NOTHING")

    #for i in range (300):
    i = 0
    while(not done):
        log("")
        log ("$$$$$$$$$ Iteration {} $$$$$$$$$".format(i))
        log("")
                
        i += 1 # ptain c'est crade
        old_state = observation
        observation, reward, done, info = env.step(chooseAction(Q, old_state))

        a = np.argmax(Q[old_state])
        Q[old_state, a] = \
                   (1 - learning_rate) * \
                   Q[old_state, a] + \
                   learning_rate * (reward + discount_rate * Q[observation, \
                                                               np.argmax(Q[observation])])

        prettyPrintQ(Q)
        log("")
        log ("$$$$$$$$$ $$$$$$$$$ $$$$$$$$$")
        log("")
        
        #log("Q matrix = {}".format(Q))

#        action = chooseAction(Q,state)
         
#        learning_rate = 0.3
#        discount_rate = 0.3
  
#        a = np.argmax(Q[state])
#        Q[state, a] = \
#            (1 - learning_rate) * \
#            Q[state, a] + \
#            learning_rate * (reward + discount_rate * Q[next_state, np.argmax(Q[next_state])])


def prettyPrintQ(Q):
    line = ["_", "\t", "_", "\t", "_"]
    labels = [
        "low & not long",
        "low & long    ",
        "med & not long",
        "med & long    ",
        "up & not long ",
        "up & long     "
        ]
    linum = 0

    log("                BUY\tSELL\tNOTHING")
    for i in range(6):
        l = line[:]
        l[np.argmax(Q[i]) * 2] = "X"
        log(labels[i] + "\t" + "".join(l))

def chooseAction(Q, state):
    ACTIONS = ['BUY', 'SELL', 'NOTHING']
    return ACTIONS[np.argmax(Q[state])]


def applyAction(current):
    ## La flemme je sais meme pas ce que je vais mettre en prototype
    ## J'ai mis current au pif, j'aurais aussi bien pu mettre diplodocus
    pass



if __name__ == "__main__":
    test_run()


""" 
Features
adjusted cose / SMA
BB value
holding stock 
return since entry (percentage) -- Not yet
"""

# normalize / discretize features 

"""
stepsize = size(data) / steps
data.sort()
for i in range (0, steps) 
    threshold[i] = data[(i + 1) * stepsize]
"""

# builds a utility table as the agent interacts w/ the world
###print np.random.normal(size=(5,4)) 
""" 
Select training data 
iterate vertme <s,a,r,s'>
- set starttime, init Q w/ random
- select a 
- observe r,s'
- update Q
test policy pi (apply it to get the state for the next val
repeat until converge 

Update Q using Bellman equation
gamma : discount rate 
alpha: learning rate
Q'[s,a] = (1 - alpha) * Q[s,a] + alpha*(r+gamma*Q[s', argmaxa'(Q[s',a']))

""" 
""" 
success depends on exploration 
choose a random action w/ proba c typically 0.3 at the beg of learning
diminish overtime to 0
""" 


