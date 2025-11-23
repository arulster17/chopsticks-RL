import sys
import csv
from collections import defaultdict
import random

import constants as C

def readQTable(filename):
    Q = defaultdict(float)
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == "STATE_ID": # header
                continue
            state_id = int(row[0])
            state_tuple = tuple([C.HAND_MAP[state_id % 15], C.HAND_MAP[state_id // 15]])
            for i in range(8):
                Q[(state_tuple, C.ALL_ACTIONS[i+1])] = float(row[i])
    return Q


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

# agent at full strength, pick optimal moves
def chooseAction(Q, state, epsilon):
    legal_actions = legalActions(state)
    # pick one of the best options
    state_tuple = tuple(state)
    best_exp_val = max(Q[(state_tuple, action)] for action in legal_actions)
    best_actions = [action for action in legal_actions if Q[(state_tuple, action)] == best_exp_val]
    return random.choice(best_actions)


if len(sys.argv) != 2:
    print("Usage: python playvsbot.py <path_to_Q_table_csv>")
    sys.exit(1)

qtable_filename = sys.argv[1]
Q = readQTable(qtable_filename)

