# Game constants
ALL_ACTIONS = ["ATTACK_LL", "ATTACK_LR", "ATTACK_RL", "ATTACK_RR",
                "SWAP_L2R", "SWAP_L1R", "SWAP_R1L", "SWAP_R2L"]
HAND_MAP = {0:(0,0), 1:(0,1), 2:(0,2), 3:(0,3), 4:(0,4), 5:(1,1), 6:(1,2), 7:(1,3), 8:(1,4), 9:(2,2), 10:(2,3), 11:(2,4), 12:(3,3), 13:(3,4), 14:(4,4)}
MAX_TURNS = 100

# RL parameters + tuning
ALPHA = 0.1
GAMMA = 1.0


P_RANDOM_MOVE = 0
STEP_PENALTY = -0.01
SPEED_BONUS_PARAM = 0.5
SPEED_BONUS = [(SPEED_BONUS_PARAM * (1.0 - turn / MAX_TURNS)) for turn in range(0, MAX_TURNS + 1)]