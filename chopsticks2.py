import random
from collections import defaultdict
import csv
import time


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


# helper to make geq 5 -> 0 and ensure lhs ≤ rhs
def normalize(tuple):
    (a,b) = tuple
    if a >= 5:
        a = 0
    if b >= 5:
        b = 0
    if a <= b:
        return (a,b)
    else:
        return (b,a)

# don't think this is ever used but whatever lol
ALL_ACTIONS = ["ATTACK_LL", "ATTACK_LR", "ATTACK_RL", "ATTACK_RR",
                "SWAP_L2R", "SWAP_L1R", "SWAP_R1L", "SWAP_R2L"]

ALPHA = 0.1
GAMMA = 1.0
MAXTURNS = 100

#state [(a,b),(c,d)] -> (a,b) current hands, (c,d) other hands
# list of legal actions at current state
def legalActions(state):
    (a,b) = state[0]
    (c,d) = state[1]
    legal_actions = []

    # check each action

    # ATTACK_LL
    if a != 0 and c != 0:
        legal_actions.append("ATTACK_LL")

    # ATTACK_LR
    if a != 0 and d != 0:
        legal_actions.append("ATTACK_LR")

    # ATTACK_RL
    if b != 0 and c != 0:
        legal_actions.append("ATTACK_RL")

    # ATTACK_RR
    if b != 0 and d != 0:
        legal_actions.append("ATTACK_RR")

    # SWAP_L2R
    if a >= 2 and b <= 2:
        legal_actions.append("SWAP_L2R")

    # SWAP_L1R
    if a >= 1 and b <= 3:
        legal_actions.append("SWAP_L1R")

    # SWAP_R1L
    if b >= 1 and a + 2 <= b: # check R can give 1 and L <= R after
        legal_actions.append("SWAP_R1L")

    # SWAP_R2L
    if b >= 2 and a + 4 <= b: # check R can give 2 and L <= R after
        legal_actions.append("SWAP_R2L")
    
    return legal_actions

def chooseAction(state, epsilon):
    legal_actions = legalActions(state)
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

# apply action to state, flip to indicate new turn
def step(state, action):
    legal_actions = legalActions(state)
    if action not in legal_actions:
        raise ValueError(f"Illegal action {action} in state {state}")

    (a,b) = state[0]
    (c,d) = state[1]

    cur_new = (a,b)
    opp_new = (c,d)
    match action:
        case "ATTACK_LL":
            opp_new = normalize((a+c, d))
        case "ATTACK_LR":
            opp_new = normalize((c, a+d))
        case "ATTACK_RL":
            opp_new = normalize((b+c, d))
        case "ATTACK_RR":
            opp_new = normalize((c, b+d))
        case "SWAP_L2R":
            cur_new = normalize((a-2, b+2))
        case "SWAP_L1R":
            cur_new = normalize((a-1, b+1))
        case "SWAP_R1L":
            cur_new = normalize((a+1, b-1))
        case "SWAP_R2L":
            cur_new = normalize((a+2, b-2))
        case _:
            raise ValueError(f"Unrecognized action {action} in state {state}")

        
    return [opp_new, cur_new]
        

def isGameOver(state):
    return state[0] == (0,0)


STEP_PENALTY = -0.01

# precompute speed bonus
SPEED_BONUS_PARAM = 0.5
SPEED_BONUS = [(SPEED_BONUS_PARAM * (1.0 - turn / MAXTURNS)) for turn in range(0, MAXTURNS + 1)]
def computeReward(next_state, turns):
    if next_state[0] == (0,0):   # opponent dead -> after swap, cur player dead
        # punish fast losses and reward fast wins
        return 1.0 + SPEED_BONUS[turns]
        #return 1.0
    # can't happen?
    # if next_state[1] == (0,0):   # you dead -> after swap, opponent is dead
    #     return -1.0
    if turns >= MAXTURNS:
        return 0.0
    return STEP_PENALTY

def run_game(epsilon):
    state = [(1,1), (1,1)]
    path = []
    for turn in range(1, MAXTURNS+1):
        if isGameOver(state):
            break

        action = chooseAction(state, epsilon)
        new_state = step(state, action)
        reward = computeReward(new_state, turn)
        path.append((state, action, reward, new_state))
        state = new_state
    
    return path

def update_Q_from_path(Q, path):
    # iterate backwards
    for (state, action, reward, new_state) in reversed(path):
        if isGameOver(new_state):
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
            target = reward - GAMMA*max(Q[(tuple(new_state), next_action)] for next_action in legalActions(new_state))

        # Q update
        # terminal
        # Q[s,a] = Q[s,a] + α(r - Q[s,a])
        # nonterminal
        # Q[s,a] = Q[s,a] + α(r - max_a' Q[s',a'] - Q[s,a])
        Q[(tuple(state), action)] += ALPHA * (target - Q[(tuple(state), action)])


def run_trials(num_trials, Q):
    start = time.time()
    eps = 1.0
    for i in range(1, num_trials+1):
        path = run_game(eps)
        update_Q_from_path(Q, path) # run once

        eps = max(0.05, eps * 0.999) # slowly decrease epsilon

        if i % 10000 == 0:
            print(f"{i} runs completed. Time elapsed: {time.time() - start:.3f}s")

    # demo game
    # path = run_game(0)
    # for move in path:
    #     print(move)


Q = defaultdict(float)
run_trials(1000000, Q)



# write q to a file to play later
# enumerate states
# easy to do with map to get hands -> (0,14)
# each row will represent actions for the state
# illegal actions will be written as 0
hand_map = {
    0  : (0,0),
    1  : (0,1),
    2  : (0,2),
    3  : (0,3),
    4  : (0,4),
    5  : (1,1),
    6  : (1,2),
    7  : (1,3),
    8  : (1,4),
    9  : (2,2),
    10 : (2,3),
    11 : (2,4),
    12 : (3,3),
    13 : (3,4),
    14 : (4,4)
}
header = ["STATE_ID"] + ALL_ACTIONS
data = []
for state_id in range(225):
    datapoint = [state_id]
    state = [hand_map[state_id % 15], hand_map[state_id // 15]]
    for action in ALL_ACTIONS:
        datapoint.append(Q[(tuple(state), action)])
    data.append(datapoint)

# write q table to file
filename = 'qtable.csv'

with open(filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(header)
    csv_writer.writerows(data)

print(f"Q-table data written to {filename}")