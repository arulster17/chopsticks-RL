import sys
import csv
from collections import defaultdict
import random
import time

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

    print(f"----------\nBOT: {opp_hands[0]} {opp_hands[1]}\n\nYOU: {cur_hands[0]} {cur_hands[1]}\n----------")

if len(sys.argv) != 2:
    print("Usage: python playvsbot.py <path_to_Q_table_csv>")
    sys.exit(1)

qtable_filename = sys.argv[1]
Q = readQTable(qtable_filename)


# simulate a game
# you can go second :)

state = [(1,1), (1,1)]
bot_goes_first = True

while True:
    if bot_goes_first:
        # show user the gamestate, need to flip since bot POV
        printGameState([state[1], state[0]])

        # if 0,0 then user wins
        if env.isGameOver(state):
            print("You win!")
            break

        # pretend to think
        time.sleep(1)
        print("Choppy is thinking...")
        time.sleep(2)

        # let bot play a move
        bot_action = chooseAction(Q, state)
        print("Choppy's move: " + bot_action)
        state = env.step(state, bot_action)

    # show user the gamestate
    printGameState(state)
    legal_actions = env.legalActions(state)

    # if 0,0 then user loses
    if env.isGameOver(state):
        print("Choppy wins!")
        break

    # get user move
    user_action = "weewoo"
    first_move = True
    while user_action not in legal_actions:
        if not first_move:
            print("Invalid move!")
        print("Valid actions: " + ", ".join(legal_actions))
        # print("Your move:", end = "")
        user_action = input("Your move: ")
        first_move = False
    
    # play user move
    state = env.step(state, user_action)
