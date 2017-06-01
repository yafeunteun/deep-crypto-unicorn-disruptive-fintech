import util as utl
import pandas as pd
import numpy as np
import math

DEBUG=True


class Environment:
    def __init__(self):
        self.data = pd.read_csv("/home/unicorn/work/datasets/rates_2017_january_may_1min.csv")
        self.state_idx = 0
        self.long_positions = False

        window = 5
        self.sma_5 = utl.get_rolling_mean(df.close, window)
        rstd_5 = utl.get_rolling_std(df.close, window)
        self.upper_band_5, self.lower_band_5 = utl.get_bollinger_bands(self.sma_5, rstd_5)

        self.returns = np.zeros(len(data))
        self.returns[1:] = (df.loc[1:, 'close'] / df['close'][:-1].values)-1


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

        isAbove = self.data.loc[self.state_idx, 'close'] > self.upper_band_5
        isBelow = self.data.loc[self.state_idx, 'close'] < self.lower_band_5
        isBetween = \
                    self.data.loc[self.state_idx, 'close'] <= self.upper_band_5 \
                    and self.data.loc[self.state_idx, 'close'] >= self.lower_band_5

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

    env = Environment()
    env.reset()

    observation, reward, done, info = env.step(None)

    print observation, reward
    
    log("Init Q w/ random values")
    Q = np.random.normal(size=(5,3))  ## 3 actions * 5 states (just to try, there will be much more")
    log("Q matrix = {}".format(Q))

#        action = chooseAction(Q,state)
         
#        learning_rate = 0.3
#        discount_rate = 0.3
  
#        a = np.argmax(Q[state])
#        Q[state, a] = \
#            (1 - learning_rate) * \
#            Q[state, a] + \
#            learning_rate * (reward + discount_rate * Q[next_state, np.argmax(Q[next_state])])

         
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


