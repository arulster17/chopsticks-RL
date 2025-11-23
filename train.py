import random
from collections import defaultdict
import csv
import time
import sys

import constants as C
import env

# states [(a,b),(c,d)], where (a,b) is your hand, (c,d) is opp hand, a <= b, c <= d
# actions
# attack
#   LL
#   LR
#   RL
#   RR
# swap

#   2 from smaller to bigger (L2R)
#       (2,2) : (0,4)
#   1 from smaller to bigger (L1R)
#       (1,1) : (0,2)
#       (1,2) : (0,3)
#       (1,3) : (0,4)
#       (2,2) : (1,3)
#       (2,3) : (1,4)
#       (3,3) : (2,4)
#   1 from bigger to smaller (R1L)
#       (0,2) : (1,1)
#       (0,3) : (1,2)
#       (0,4) : (1,3)
#       (1,3) : (2,2)
#       (1,4) : (2,3)
#       (2,4) : (3,3)
#   2 from bigger to smaller (R2L)
#       (0,4) : (2,2)


# occasionally force random move to cover more cases in self-play
def chooseActionTraining(Q, state, epsilon):
    state_tuple = tuple(state)
    actions = env.legalActions(state_tuple)
    if random.random() < C.P_RANDOM_MOVE:
        return random.choice(actions)

    return chooseAction(Q, state, epsilon)

def chooseAction(Q, state, epsilon):
    legal_actions = env.legalActions(state)
    if (len(legal_actions) == 0):
        raise ValueError(f"Called chooseAction with state {state}, which has no legal actions")
    if random.random() < epsilon:
        # pick random action
        return random.choice(legal_actions)
    else:
        # pick one of the best options
        state_tuple = tuple(state)
        best_exp_val = max(Q[(state_tuple, action)] for action in legal_actions)
        best_actions = [action for action in legal_actions if Q[(state_tuple, action)] == best_exp_val]
        return random.choice(best_actions)

def computeReward(next_state, turns):
    if next_state[0] == (0,0):   # opponent dead -> after swap, cur player dead
        # punish fast losses and reward fast wins
        return 1.0 + C.SPEED_BONUS[turns]
        #return 1.0
    # can't happen?
    # if next_state[1] == (0,0):   # you dead -> after swap, opponent is dead
    #     return -1.0
    if turns >= C.MAX_TURNS:
        return 0.0
    return C.STEP_PENALTY

def run_game(Q, epsilon):
    state = [(1,1), (1,1)]
    path = []
    for turn in range(1, C.MAX_TURNS+1):
        if env.isGameOver(state):
            break

        # USE ACTION CHOICE THAT FORCES A FEW MORE RANDOM CHOICES
        # THIS IS KINDA LIKE INCREASING EPSILON
        action = chooseActionTraining(Q, state, epsilon)
        new_state = env.step(state, action)
        reward = computeReward(new_state, turn)
        path.append((state, action, reward, new_state))
        state = new_state
    
    return path

def update_Q_from_path(Q, path):
    # iterate backwards
    for (state, action, reward, new_state) in reversed(path):
        if env.isGameOver(new_state):
            # if terminal then set winner
            target = reward
        else:
            # this is a two player zero sum game
            # thus if my opponent has V(s) from a state they are about to play from, my value is -V(s)
            # assuming the opponent plays optimally
            # bellman update:
            # Q(s,a) = r + γ(future value)
            # Q(s,a) = r + γ(-V(s'))
            # Q(s,a) = r + γ(-max_a' Q(s',a'))
            # reverses the bellman in a way from what i understand
            # this would be good to write in our milestone
            target = reward - C.GAMMA*max(Q[(tuple(new_state), next_action)] for next_action in env.legalActions(new_state))

        # Q update
        # terminal
        # Q[s,a] = Q[s,a] + α(r - Q[s,a])
        # nonterminal
        # Q[s,a] = Q[s,a] + α(r - max_a' Q[s',a'] - Q[s,a])
        Q[(tuple(state), action)] += C.ALPHA * (target - Q[(tuple(state), action)])


def run_trials(num_trials, Q):
    start = time.time()
    epsilon = 1.0
    for i in range(1, num_trials+1):
        path = run_game(Q, epsilon)
        update_Q_from_path(Q, path) # run once

        epsilon = max(0.05, epsilon * 0.999) # slowly decrease epsilon

        if i % 10000 == 0:
            print(f"{i} runs completed. Time elapsed: {time.time() - start:.3f}s")


def writeQTableToFile(Q, filename):
    # write q to a file to play later
    # enumerate states
    # easy to do with map to get hands -> (0,14)
    # each row will represent actions for the state
    # illegal actions will be written as 0

    header = ["STATE_ID"] + C.ALL_ACTIONS
    data = []
    for state_id in range(225):
        datapoint = [state_id]
        state = [C.HAND_MAP[state_id % 15], C.HAND_MAP[state_id // 15]]
        for action in C.ALL_ACTIONS:
            datapoint.append(Q[(tuple(state), action)])
        data.append(datapoint)

    # write q table to file
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)
        csv_writer.writerows(data)

    print(f"Q-table data written to {filename}")


def main():
    if len(sys.argv) != 3:
        print("usage: python train.py <num_trials> <path_to_output_csv>")
        sys.exit(1)

    num_trials = int(sys.argv[1])
    filename = sys.argv[2]
    Q = defaultdict(float)
    run_trials(num_trials, Q)
    writeQTableToFile(Q, filename)


if __name__ == "__main__":
    main()