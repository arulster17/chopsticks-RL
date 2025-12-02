import random
from collections import defaultdict
import csv
import time
import sys
import matplotlib.pyplot as plt

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


def simulateGamesVsPast(Q, Q_prev):
    # simulate 1000 games vs random and return winrate
    gamesWon = 0
    gamesDrawn = 0
    gamesLost = 0
    for game in range(1000):
        # simulate random game, start first half the times
        state = [(1,1), (1,1)]
        moves = 0
        if game % 2 == 0:
            # random start
            # play prev move
            prev_bot_action = chooseAction(Q, state, 0) # pick bot's best choice
            state = env.step(state, prev_bot_action)
            moves += 1
        while moves < C.MAX_TURNS:
            ### check random wins
            if env.isGameOver(state):
                gamesLost += 1
                break
            # play bot move
            bot_action = chooseAction(Q, state, 0) # pick bot's best choice
            state = env.step(state, bot_action)
            moves += 1
            if (moves >= C.MAX_TURNS):
                break
            # check bot win
            if env.isGameOver(state):
                gamesWon += 1
                break
            # play prev move
            prev_bot_action = chooseAction(Q, state, 0) # pick bot's best choice
            state = env.step(state, prev_bot_action)
            moves += 1
        if moves == C.MAX_TURNS:
            gamesDrawn += 1
    return (gamesWon, gamesDrawn, gamesLost)

# euclidean distance
def matrixDiff(Q, Q_prev):
    ans = 0.0
    for key in Q.keys():
        ans += (Q[key] - Q_prev[key])**2
    return ans**0.5

def run_trials(num_trials, Q):
    qchange = []
    start = time.time()
    epsilon = 1.0
    Q_prev = Q.copy()
    for i in range(1, num_trials+1):
        path = run_game(Q, epsilon)
        update_Q_from_path(Q, path) # run once

        epsilon = max(0.05, epsilon * 0.999) # slowly decrease epsilon
        
        if i % (num_trials / 100) == 0:
            print(f"{i} runs completed. Time elapsed: {time.time() - start:.3f}s")
            # compute difference to previous Q then update
            qchange.append(matrixDiff(Q,Q_prev))
            Q_prev = Q.copy()
    return qchange
            


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
    qchange = run_trials(num_trials, Q)
    

    plt.plot(range(len(qchange)), qchange)
    plt.xlabel(f"Checkpoint (#episodes ≈ {num_trials//100} per step)")
    plt.ylabel("L2 distance between Q and previous Q")
    plt.title("Q-learning convergence: change in Q-values over training")
    plt.show()

    
    writeQTableToFile(Q, filename)




if __name__ == "__main__":
    main()