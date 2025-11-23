import random

NUM_PLAYERS = 2           # fixed at 2 here
NUM_GAMES = 20000         # training episodes
MAX_TURNS = 200           # safety cap to avoid infinite loops
STEP_PENALTY = -0.01      # punish long games
ALPHA = 0.1               # learning rate
GAMMA = 1.0               # discount

VALID_SWAPS = { 
    (0,0) : [],

    (0,1) : [],

    (0,2) : [(1,1)],
    (1,1) : [(0,2)],

    (0,3) : [(1,2)],
    (1,2) : [(0,3)],

    (0,4) : [(1,3), (2,2)],
    (1,3) : [(0,4), (2,2)],
    (2,2) : [(0,4), (1,3)],

    (1,4) : [(2,3)],
    (2,3) : [(1,4)],

    (2,4) : [(3,3)],
    (3,3) : [(2,4)],

    (3,4) : [],
    (4,4) : [],
}

def normalize(hand):
    a, b = hand
    if a >= 5: a = 0
    if b >= 5: b = 0
    return (a, b) if a <= b else (b, a)

# ---------- ACTIONS ----------

def get_legal_actions(state):
    """Return list of valid actions in given state.
       State = ((me_L, me_R), (opp_L, opp_R))
       Actions:
         ('swap', new_L, new_R)
         ('atk', my_hand_index, opp_hand_index)
    """
    (me, opp) = state
    me = normalize(me)
    opp = normalize(opp)

    # if I'm dead, no actions (should be terminal already)
    if me == (0,0):
        return []

    actions = []

    # swaps
    for new_hand in VALID_SWAPS[me]:
        actions.append(('swap', new_hand[0], new_hand[1]))

    # attacks
    me_hands = [me[0], me[1]]
    opp_hands = [opp[0], opp[1]]
    for my_idx in range(2):
        if me_hands[my_idx] == 0:
            continue
        for opp_idx in range(2):
            if opp_hands[opp_idx] == 0:
                continue
            actions.append(('atk', my_idx, opp_idx))

    return actions

def step(state, action):
    """Apply action to state.
       Returns: next_state (already rotated), reward, done(bool)
       State is always from POV of player to move.
    """
    (me, opp) = state
    me = normalize(me)
    opp = normalize(opp)

    kind = action[0]

    if kind == 'swap':
        _, newL, newR = action
        new_me = normalize((newL, newR))
        new_opp = opp
    else:  # 'atk'
        _, my_idx, opp_idx = action
        me_list = [me[0], me[1]]
        opp_list = [opp[0], opp[1]]

        value = me_list[my_idx]
        opp_list[opp_idx] = (opp_list[opp_idx] + value) % 5

        new_me = normalize(tuple(me_list))
        new_opp = normalize(tuple(opp_list))

    # terminal checks BEFORE rotation
    if new_opp == (0,0) and new_me != (0,0):
        # I killed opponent -> win
        return (new_me, new_opp), 1.0, True
    if new_me == (0,0) and new_opp != (0,0):
        # I killed myself somehow -> loss
        return (new_me, new_opp), -1.0, True
    if new_me == (0,0) and new_opp == (0,0):
        # simultaneous death -> draw
        return (new_me, new_opp), 0.0, True

    # non-terminal: step penalty and rotate POV to next player
    reward = STEP_PENALTY
    next_state = (new_opp, new_me)  # opponent becomes "me" next turn
    return next_state, reward, False

# ---------- Q-TABLE & POLICY ----------

def ensure_state_in_q(qtable, state):
    if state not in qtable:
        actions = get_legal_actions(state)
        qtable[state] = {a: 0.0 for a in actions}

def choose_action(qtable, state, epsilon):
    ensure_state_in_q(qtable, state)
    actions = list(qtable[state].keys())

    # if somehow no actions, return None
    if not actions:
        return None

    if random.random() < epsilon:
        return random.choice(actions)

    # greedy
    qs = qtable[state]
    max_q = max(qs.values())
    best_actions = [a for a, q in qs.items() if q == max_q]
    return random.choice(best_actions)

def run_episode(qtable, epsilon, verbose=False):
    # initial symmetric state: both players (1,1)
    state = ((1,1), (1,1))
    total_reward = 0.0

    for t in range(MAX_TURNS):
        actions = get_legal_actions(state)
        if not actions:
            # no moves -> treat as draw
            if verbose:
                print("No legal actions, terminating.")
            break

        action = choose_action(qtable, state, epsilon)
        next_state, reward, done = step(state, action)
        total_reward += reward

        # Q-learning update
        ensure_state_in_q(qtable, state)
        old_q = qtable[state][action]

        if done:
            target = reward
        else:
            ensure_state_in_q(qtable, next_state)
            max_next = max(qtable[next_state].values()) if qtable[next_state] else 0.0
            target = reward + GAMMA * max_next

        qtable[state][action] = old_q + ALPHA * (target - old_q)

        if verbose:
            print(f"t={t}, state={state}, action={action}, "
                  f"reward={reward:.2f}, next={next_state}, done={done}")

        state = next_state
        if done:
            break

    # infer “winner” from last state (non-rotated), for logging only
    (me, opp) = state
    if opp == (0,0) and me != (0,0):
        winner = 0  # player who just moved in original orientation
    elif me == (0,0) and opp != (0,0):
        winner = 1
    else:
        winner = -1  # draw/timeout/unknown

    if verbose:
        print("Episode finished, winner:", winner, "total_reward:", total_reward)

    return winner

def train():
    qtable = {}
    epsilon = 1.0
    EPS_MIN = 0.05
    DECAY = 0.9999

    wins = {0: 0, 1: 0, -1: 0}

    print("Starting training...")
    for ep in range(1, NUM_GAMES + 1):
        winner = run_episode(qtable, epsilon, verbose=False)
        wins[winner] += 1

        # decay epsilon
        epsilon = max(EPS_MIN, epsilon * DECAY)

        if ep % 1000 == 0:
            print(f"Episode {ep}, epsilon={epsilon:.3f}, "
                  f"wins: P0={wins[0]}, P1={wins[1]}, draws={wins[-1]}")

    print("Training complete.")
    return qtable

def demo(qtable, num_games=3):
    print("\nDemo with greedy policy (epsilon=0):")
    for g in range(num_games):
        print(f"\nGame {g+1}")
        run_episode(qtable, epsilon=0.0, verbose=True)

if __name__ == "__main__":
    q = train()
    demo(q)
