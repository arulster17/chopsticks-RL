# all the program stuff here

numplayers = 2 # number of players
maxturns = 100 # maximum turns

# state will be n+1 length list where first n are 2d tuples
# for n = 2, will be [(p1 LH, p1 RH), (p2 LH, p2 RH), moveCounter]

# internally enforce LH <= RH for all pairs
# disallow moves like (3,4) -> (2,5) -> (2,0)

# get list of allowed swaps given sum
VALID_SWAPS = [ [], # 0
                [(0,1)], # 1
                [(0,2), (1,1)], # 2
                [(0,3), (1,2)], # 3
                [(0,4), (1,3), (2,2)], # 4
                [(1,4), (2,3)], # 5
                [(2,4), (3,3)], # 6
                [(3,4)], # 7
                [(4,4)] # 8
            ]


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


# list of states available from current state
def stateactions(currentstate):
    newstatelist = []
    # swap for moveCounter % n
    movecounter = currentstate[-1]
    curplayerindex = movecounter % numplayers
    playerhands = currentstate[curplayerindex]

    # if playerhands = (0,0), they are eliminated, just skip and increment term
    if playerhands == (0,0):
        newstate = currentstate.copy()
        newstate[-1] += 1
        return [newstate]
    
    candidate_swaps = VALID_SWAPS[playerhands]
    for cand in candidate_swaps:
        newstate = currentstate.copy()
        newstate[curplayerindex] = cand
        newstate[-1] += 1
        newstatelist.append(newstate)
    return newstatelist


print(stateactions([(0,0),(1,1),4]))
