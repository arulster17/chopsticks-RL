import itertools
import random

# all the program stuff here

num_players = 2 # number of players
max_turns = 100 # maximum turns, maximum move is max_turns so the 100 moves are 0->1 to 99->100
num_games = 10000 # number of games simulated

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
def getAllNextStates(state):
    current_state = state.copy()
    new_state_list = []
    # swap for moveCounter % n
    move_counter = current_state[-1]
    cur_player_index = move_counter % num_players
    player_hands = current_state[cur_player_index]

    current_state[-1] += 1 # increment moves for all answers

    # if player_hands = (0,0), they are eliminated, just skip and increment term
    if player_hands == (0,0):
        new_state = current_state.copy()
        return [new_state]
    
    # add swaps
    candidate_swaps = VALID_SWAPS[player_hands]
    for cand in candidate_swaps:
        new_state = current_state.copy()
        new_state[cur_player_index] = cand
        new_state_list.append(new_state)

    # add attacks
    (a,b) = player_hands
    for i in range(num_players):
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
            new_state_list.append(new_state)

    return new_state_list

# compute a dictionary of all states to actions+weights, initialize weights to 1
def initializeQTable():
    # generate a list of all states using itertools
    # for n players we want the cartesian product of n players and the move counter
    all_hands = VALID_SWAPS.keys() # lazy trick lol
    all_move_counters = list(range(0, max_turns))
    lists = [all_hands]*num_players + [all_move_counters]

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

# returns -3 if all eliminated somehow, -2 if max_turns reached, -1 if game is not over, else returns winner index
def checkGameStatus(current_state):
    num_turns = current_state[-1]
    hands = current_state[:-1]

    # if past last turn
    if num_turns > max_turns:
        return -2

    found_alive = False
    first_winner = -1
    for i,hand in enumerate(hands):
        if hand != (0,0):
            if found_alive == True:
                # check if game is over by length
                # having this here means that if a player wins on the last available move, they get the win
                # not sure if this check is actually necessary
                if num_turns == max_turns:
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

# get next state
def getNextState(qtable, current_state):
    #for i in qtable:
    #    print(i)
    next_weights = qtable[tuple(current_state)]
    cand_states = list(next_weights.keys())
    cand_weights = list(next_weights.values())

    # random.choices actually does the weighted sampling goated function
    chosen_state = random.choices(cand_states, weights=cand_weights, k=1)[0]
    return list(chosen_state)

# run one iteration of the game
def runGame(qtable):
    # set initial state
    state = [(1,1)]*num_players + [0]
    game_path = [state]
    game_status = checkGameStatus(state)
    while(game_status == -1): # until game end
        # sample new state from the qtable
        print(state)
        state = getNextState(qtable, state)
        game_path.append(state)
        game_status = checkGameStatus(state)
    print(state)
    print("Winner: " + str(game_status))


qtable = initializeQTable()
runGame(qtable)
# d = qtable[tuple([(1,1),(1,3),0])]
# for entry in d:
#     print(str(entry) + ": " + str(d[entry]))

# print(checkGameStatus([(0,0),(1,0),1]))

