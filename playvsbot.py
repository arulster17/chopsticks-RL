import sys
import csv
from collections import defaultdict
import random

import constants as C
import env

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
                Q[(state_tuple, C.ALL_ACTIONS[i])] = float(row[i+1])
    return Q


# agent at full strength, pick optimal moves
def chooseAction(Q, state):
    legal_actions = env.legalActions(state)
    # pick one of the best options
    state_tuple = tuple(state)
    best_exp_val = max(Q[(state_tuple, action)] for action in legal_actions)
    best_actions = [action for action in legal_actions if Q[(state_tuple, action)] == best_exp_val]
    return random.choice(best_actions)

def printGameState(state):
    cur_hands = state[0]
    opp_hands = state[1]

    print(f"BOT: {opp_hands[0]} {opp_hands[1]}\n\nYOU: {cur_hands[0]} {cur_hands[1]}")

if len(sys.argv) != 2:
    print("Usage: python playvsbot.py <path_to_Q_table_csv>")
    sys.exit(1)

qtable_filename = sys.argv[1]
Q = readQTable(qtable_filename)
printGameState([(1,3),(2,4)])


# simulate a game
# you can go second :)
state = [(1,1), (1,1)]
while True:
    # let bot play a move
    state = 3
