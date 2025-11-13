# all the program stuff here

numplayers = 2 # number of players
maxturns = 100 # maximum turns

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
        # could precompute this
        candidate_atks = {normalize((a+c,d)), normalize((b+c,d)), normalize((c,a+d)), normalize((c,b+d))}
        for cand in candidate_atks:
            newstate = currentstate.copy()
            newstate[i] = cand
            newstatelist.append(newstate)

    return newstatelist


print(stateactions([(1,1),(1,1),0]))
