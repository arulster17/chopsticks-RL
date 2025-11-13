import itertools

# all the program stuff here

numplayers = 2 # number of players
maxturns = 100 # maximum turns, maximum move is maxturns-1 so the 100 moves are 0 to 99
numgames = 10000 # numgames

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
def stateactions(currentstate):
    newstatelist = []
    # swap for moveCounter % n
    movecounter = currentstate[-1]
    curplayerindex = movecounter % numplayers
    playerhands = currentstate[curplayerindex]

    currentstate[-1] += 1 # increment moves for all answers

    # if playerhands = (0,0), they are eliminated, just skip and increment term
    if playerhands == (0,0):
        newstate = currentstate.copy()
        return [newstate]
    
    # add swaps
    candidate_swaps = VALID_SWAPS[playerhands]
    for cand in candidate_swaps:
        newstate = currentstate.copy()
        newstate[curplayerindex] = cand
        newstatelist.append(newstate)

    # add attacks
    (a,b) = playerhands
    for i in range(numplayers):
        if i == curplayerindex:
            continue
        # if our player has hands a b and opponent has c d
        # candidate hands should be a+c,d | b+c,d | c, a+d | c, b+d
        # if any entry is geq 5, make it 0 and normalize

        (c,d) = currentstate[i]

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
            newstate = currentstate.copy()
            newstate[i] = cand
            newstatelist.append(newstate)

    return newstatelist

# compute a dictionary of all states to actions+weights, initialize weights to 1
def initializeQTable():
    # generate a list of all states using itertools
    # for n players we want the cartesian product of n players and the move counter
    all_hands = VALID_SWAPS.keys() # lazy trick lol
    all_move_counters = list(range(0, maxturns))
    lists = [all_hands]*numplayers + [all_move_counters]

    product_iter = itertools.product(*lists)
    all_states = [list(t) for t in product_iter]

    # create q table
    # keys: states
    # values: dict of (newstates, weights)
    # need to convert states from list to tuples because you cannot hash lists
    d = {}
    for state in all_states: # for all states
        state_tuple = tuple(state)
        d[state_tuple] = {} # initialize weight dict
        next_states = stateactions(state) # get all next states
        statemap = d[state_tuple]
        for ns in next_states: # for all next states
            statemap[tuple(ns)] = 1 # set default weight to 1
    return d

# returns -3 if all eliminated somehow, -2 if maxturns reached, -1 if game is not over, else returns winner index
# CURRENTLY DOES NOT CONSIDER MOVE COUNTER
def checkGameStatus(currentstate):
    numturns = currentstate[-1]
    hands = currentstate[:-1]

    foundalive = False
    firstWinner = -1
    for i,hand in enumerate(hands):
        if hand != (0,0):
            if foundalive == True:
                # check if game is over by length
                # having this here means that if a player wins on the last available move, they get the win
                if numturns >= maxturns:
                    return -2
                return -1 # found two alive players, game not over
            
            # first alive player found
            foundalive = True
            firstWinner = i

    # if somehow all players are eliminated
    if not foundalive:
        return -3
    # if we get here, only 1 found alive, so they win, return firstWinner    
    return firstWinner

# qtable = initializeQTable()


# d = qtable[tuple([(1,1),(1,3),0])]
# for entry in d:
#     print(str(entry) + ": " + str(d[entry]))

print(checkGameStatus([(0,0),(1,0),100]))

#print(stateactions([(1,1),(1,0),0]))
