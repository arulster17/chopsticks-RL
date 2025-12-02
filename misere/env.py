# environment helper functions

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

# is the game over
def isGameOver(state):
    return state[0] == (0,0)