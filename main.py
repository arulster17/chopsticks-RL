import itertools
import random

# Notes:
# I'm not super confident about the computeReward, getNextState updateQtable functions
# used https://www.geeksforgeeks.org/machine-learning/q-learning-in-python/# for most of it



NUM_PLAYERS = 2 # number of players
MAX_TURNS = 100 # maximum turns, maximum move is MAX_TURNS so the 100 moves are 0->1 to 99->100
NUM_TRIALS = 10000000 # number of games simulated
STEP_PENALTY = -0.01 # penalty for longer games, need to mess around with this
ALPHA = 0.1
GAMMA = 1.0


# state will be n+1 length list where first n are 2d tuples
# for n = 2, will be [(p1 LH, p1 RH), (p2 LH, p2 RH), moveCounter]

# internally enforce LH <= RH for all pairs
# disallow moves like (3,4) -> (2,5) -> (2,0)

# get list of allowed swaps given hands
VALID_SWAPS = { 
    (0,0) : [], # 0

    (0,1) : [], # 1

    (0,2) : [(1,1)], # 2
    (1,1) : [(0,2)], # 2

    (0,3) : [(1,2)], # 3
    (1,2) : [(0,3)], # 3

    (0,4) : [(1,3), (2,2)], # 4
    (1,3) : [(0,4), (2,2)], # 4
    (2,2) : [(0,4), (1,3)], # 4

    (1,4) : [(2,3)], # 5
    (2,3) : [(1,4)], # 5

    (2,4) : [(3,3)], # 6
    (3,3) : [(2,4)], # 6

    (3,4) : [], # 7

    (4,4) : [] # 8
}

# helper to make geq 5 -> 0 and ensure lhs < rhs
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

# list of states available from current state
def getAllNextStates(current_state):
    new_state_list = []
    # swap for moveCounter % n
    move_counter = current_state[-1]
    cur_player_index = move_counter % NUM_PLAYERS
    player_hands = current_state[cur_player_index]

    # if player_hands = (0,0), they are eliminated, just skip and increment term
    if player_hands == (0,0):
        new_state = current_state.copy()
        new_state[-1] += 1
        return [new_state]
    
    # add swaps
    candidate_swaps = VALID_SWAPS[player_hands]
    for cand in candidate_swaps:
        new_state = current_state.copy()
        new_state[cur_player_index] = cand
        new_state[-1] += 1
        new_state_list.append(new_state)

    # add attacks
    (a,b) = player_hands
    for i in range(NUM_PLAYERS):
        if i == cur_player_index:
            continue
        # if our player has hands a b and opponent has c d
        # candidate hands should be a+c,d | b+c,d | c, a+d | c, b+d
        # if any entry is geq 5, make it 0 and normalize

        (c,d) = current_state[i]

        # could precompute this or maybe at least write this better lol
        candidate_atks = set()
        if a != 0:
            if c != 0:
                candidate_atks.add(normalize((a+c,d)))
            if d != 0:
                candidate_atks.add(normalize((c,a+d)))
        if b != 0:
            if c != 0:
                candidate_atks.add(normalize((b+c,d)))
            if d != 0:
                candidate_atks.add(normalize((c,b+d)))

        
        for cand in candidate_atks:
            new_state = current_state.copy()
            new_state[i] = cand
            new_state[-1] += 1
            new_state_list.append(new_state)

    return new_state_list

# compute a dictionary of all states to actions+weights, initialize weights to 1
def initializeQTable():
    # generate a list of all states using itertools
    # for n players we want the cartesian product of n players and the move counter
    all_hands = VALID_SWAPS.keys() # lazy trick lol
    all_move_counters = list(range(0, MAX_TURNS))
    lists = [all_hands]*NUM_PLAYERS + [all_move_counters]

    product_iter = itertools.product(*lists)
    all_states = [list(t) for t in product_iter]

    # create q table
    # keys: states
    # values: dict of (new_states, weights)
    # need to convert states from list to tuples because you cannot hash lists
    qtable = {}
    for state in all_states: # for all states
        state_tuple = tuple(state)
        qtable[state_tuple] = {} # initialize weight dict
        next_states = getAllNextStates(state) # get all next states
        state_map = qtable[state_tuple]
        for ns in next_states: # for all next states
            state_map[tuple(ns)] = 1 # set default weight to 1
    return qtable

# returns -3 if all eliminated somehow, -2 if MAX_TURNS reached, -1 if game is not over, else returns winner index
def checkGameStatus(current_state):
    num_turns = current_state[-1]
    hands = current_state[:-1]

    # if past last turn
    if num_turns > MAX_TURNS:
        return -2

    found_alive = False
    first_winner = -1
    for i,hand in enumerate(hands):
        if hand != (0,0):
            if found_alive == True:
                # check if game is over by length
                # having this here means that if a player wins on the last available move, they get the win
                # not sure if this check is actually necessary
                if num_turns == MAX_TURNS:
                    return -2
                return -1 # found two alive players, game not over
            
            # first alive player found
            found_alive = True
            first_winner = i

    # if somehow all players are eliminated
    if not found_alive:
        return -3
    # if we get here, only 1 found alive, so they win, return first_winner
    return first_winner

# get next state using epsilon greedy 
def getNextState(qtable, current_state, epsilon):
    # pick highest with probability 1-epsilon
    # pick random otherwise
    next_weights = qtable[tuple(current_state)]
    cand_states = list(next_weights.keys())
    cand_weights = list(next_weights.values())

    if random.random() < epsilon:
        # random
        chosen_state = random.choice(cand_states)
    else:
        # pick best
        best_weight = max(cand_weights)
        best_states = [s for s,w in next_weights.items() if w == best_weight]
        # pick randomly from one of the best
        chosen_state = random.choice(best_states)

    return list(chosen_state)

def computeReward(old_state, new_state):
    game_status = checkGameStatus(new_state)
    current_player = old_state[-1] % NUM_PLAYERS

    if game_status in {-1,-2,-3}: # game not over / draw / all eliminated somehow
        base = 0.0
    else: # someone won, was it me?
        base = 1.0 if game_status == current_player else -1.0
    
    return base + STEP_PENALTY

def updateQtable(qtable, old_state, next_state, reward):
    os = tuple(old_state)
    ns = tuple(next_state)

    cur_weight = qtable[os][ns]
    next_states = qtable.get(ns, {}) # careful near end

    if next_states:
        best_next = max(next_states.values()) # pick the highest Q value in the next states
    else:
        best_next = 0.0 # terminal value, no more rewards ahead to worry about
    
    qtable[os][ns] = cur_weight + ALPHA * (reward + GAMMA*best_next - cur_weight) 

# run one iteration of the game
def runGame(qtable, epsilon, printresults):
    # set initial state
    state = [(1,1)]*NUM_PLAYERS + [0]
    game_path = [state]
    game_status = checkGameStatus(state)

    while(game_status == -1): # until game end
        # choose next state
        next_state = getNextState(qtable, state, epsilon)

        # compute reward
        reward = computeReward(state, next_state)

        # update q table
        updateQtable(qtable, state, next_state, reward)

        # move on
        state = next_state
        game_status = checkGameStatus(state)
        game_path.append(state)
    
    if (printresults):
        for state in game_path:
            print(state)
        print("Winner: " + str(game_status))

def runTrials(num_trials):
    qtable = initializeQTable()
    print("Starting Training!")
    epsilon = 1
    for i in range(1,num_trials+1):
        if i % 100 == 0:
            print(str(i) + " trials completed.")

        runGame(qtable, epsilon, False)

        # as we go through the trials we want to prioritize exploitation over exploration -> lower epsilon
        # slowly decay epsilon
        epsilon *= 0.999
        epsilon = max(epsilon, 0.05) # dont let it get too low
    
    # demonstrate a few games after learning, play best moves
    print("Training Complete!")
    for i in range(5):
        runGame(qtable, 0.0, True)
    
    # return final table
    return qtable


runTrials(NUM_TRIALS)