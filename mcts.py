import random
import math
import collections

Outcome = collections.namedtuple('Outcome', ['wins', 'draws', 'losses'])

OUTCOME_NONE = Outcome(wins = 0, draws = 0, losses = 0)
OUTCOME_WIN  = Outcome(wins = 1, draws = 0, losses = 0)
OUTCOME_DRAW = Outcome(wins = 0, draws = 1, losses = 0)
OUTCOME_LOSS = Outcome(wins = 0, draws = 0, losses = 1)

class GameState:
    """MT search tree node.

       Holds the game state, explored moves and aggreagated game outcome for the subtree.
    """

    # Outcomes for the subtree, default is all zeroes.
    outcome = OUTCOME_NONE

    def __init__(self):
        # Map freedom to child game state for explored states
        self.explored = dict()

    def freedoms(self):
        # Number of moves in this position.
        # Should be 0 for the leaf state.
        raise ENotImplementedError

    def createChild(self, freedom):
        # Create child GameState for a particular move.
        raise ENotImplementedError

    def readChildOutcome(self, child):
        # Allow to reinterpret child outcome for turn based games where child win is the parent loss.
        # By default returning child outcome as is.
        return child.outcome

    def incrementOutcome(self, child, delta):
        # Increment outcome for this state by delta outcome for the child state.
        # Returns delta applied to this game state.
        self.outcome = Outcome(*(x + y for x, y in zip(self.outcome, delta)))
        return delta

    def tensors(self):
        # Return game state as a list of 3D numpy tensors
        raise ENotImplementedError

    @staticmethod
    def model(cls):
        raise ENotImplementedError

    def getChildByFreedom(self, freedom):
        # Get explored child game state for the move or create new one.
        if freedom not in self.explored:
            self.explored[freedom] = self.createChild(freedom)
        return self.explored[freedom]


class GameStrategy:
    """Play strategy.

       For a given game state:
       strategy.explore(state)  # explore possible moves first
       state = strategy.move(state)  # pick a move and return new state
    """
    def explore(self, game_state):
        # Explore plays
        raise ENotImplementedError

    def chooseMove(self, game_state):
        # Return best move freedom index for the <game_state> during play
        raise ENotImplementedError

    def rolloutMove(self, game_state):
        # Return best move freedom index for the <game_state> during rollout
        return self.chooseMove(game_state)

    def move(self, game_state):
        # Pick a move from available game_state moves and return new tuple: (freedom, new_game_state).
        freedom = self.chooseMove(game_state)
        return freedom, game_state.getChildByFreedom(freedom)

    def rollout(self, game_state):
        # Rollout game play, assume small depth for now
        stack = [game_state]
        freedoms = game_state.freedoms()
        while freedoms:
            stack.append(stack[-1].getChildByFreedom(self.rolloutMove(stack[-1])))
            freedoms = stack[-1].freedoms()

        # Update outcome
        delta = Outcome(*(min(1, x) for x in stack[-1].outcome))
        child = stack[-1]
        for item in reversed(stack[:-1]):
            delta = item.incrementOutcome(child, delta)
            child = item


class RandomGameStrategy(GameStrategy):
    """ Random play strategy.

        Playing <tryouts> random games.
    """
    def __init__(self, tryouts):
        self.tryouts = tryouts

    def explore(self, game_state):
        # On the first explore call try a number of random plays
        for i in range(self.tryouts):
            self.rollout(game_state)

    def rolloutMove(self, game_state):
        freedoms = game_state.freedoms()
        if freedoms:
            return random.randint(0, freedoms - 1)
        return None

    def chooseMove(self, game_state):
        t = 2 * math.log(sum(sum(game_state.readChildOutcome(x)) for x in game_state.explored.values()))
        best = None
        for freedom, state in game_state.explored.items():
            outcome = game_state.readChildOutcome(state)
            n = sum(outcome)
            cost = outcome.wins / n + math.sqrt(t / n)
            if best is None or best_cost < cost:
                best = freedom
                best_cost = cost
        return best


class UCTGameStrategy(GameStrategy):
    """ Random play strategy.

        Playing <tryouts> random games.
    """
    def __init__(self, tryouts):
        self.tryouts = tryouts

    def explore(self, game_state):
        # On the first explore call try a number of random plays
        for i in range(self.tryouts):
            self.rollout(game_state)

    def chooseMove(self, game_state):
        freedoms = game_state.freedoms()
        outcomes = [game_state.readChildOutcome(game_state.getChildByFreedom(i)) for i in range(freedoms)]
        total = 1 + sum(sum(x) for x in outcomes)
        t = 2 * math.log(total)
        best = []
        for freedom, state in enumerate(outcomes):
            n = 1 + sum(outcomes[freedom])
            cost = (outcomes[freedom].wins - outcomes[freedom].losses) / n + math.sqrt(t / n)
            if not best or best_cost < cost:
                best = [freedom]
                best_cost = cost
            elif best_cost == cost:
                best.append(freedom)
        return best[random.randint(0, len(best)-1)]

