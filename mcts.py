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

    def tensors(self):
        # Return game state as a list of 3D numpy tensors
        raise ENotImplementedError

    @staticmethod
    def model(cls):
        raise ENotImplementedError

    def getChildByFreedom(self, freedom):
        # Get explored child game state for the move or create new one.
        if freedom not in self.explored:
            ch = self.createChild(freedom)
            # New child state might be a leaf node, update stats if that's the case.
            self.outcome = Outcome(*(x + y for x, y in zip(self.outcome, ch.outcome)))
            self.explored[freedom] = ch
            return ch
        else:
            return self.explored[freedom]
        
    def exploreMove(self, strategy, freedom):
        # Explore single move using given strategy

        ch = self.getChildByFreedom(freedom)
        original_outcome = ch.outcome

        strategy.exploreMove(ch)

        if not (ch.outcome is original_outcome):
            # Update outcome by the change in the child outcome
            self.outcome = Outcome(*(x + y - z for x, y, z in zip(self.outcome, ch.outcome, original_outcome)))


class GameStrategy:
    """Play strategy.

       For a given game state:
       strategy.explore(state)  # explore possible moves first
       state = strategy.move(state)  # pick a move and return new state
    """
    def explore(self, game_state):
        # Explore plays
        raise ENotImplementedError

    def exploreMove(self, game_state):
        # Recursive exploration from GameState
        raise ENotImplementedError

    def move(self, game_state, maximize='wins'):
        # Pick a move from available game_state moves and return new tuple: (freedom, new_game_state).
        assert maximize in Outcome._fields
        raise ENotImplementedError


class RandomGameStrategy(GameStrategy):
    """ Random play strategy.

        Playing <tryouts> random games.
    """
    def __init__(self, tryouts):
        self.tryouts = tryouts

    def exploreMove(self, game_state):
        # Just executing random moves without considering odds of each move to happen
        freedoms = game_state.freedoms()
        if freedoms:
            game_state.exploreMove(self, random.randint(0, freedoms-1))

    def explore(self, game_state):
        # On the first explore call try a number of random plays
        for i in range(self.tryouts):
            self.exploreMove(game_state)

    def move(self, game_state, maximize='wins'):
        t = 2 * math.log(sum(sum(x.outcome) for x in game_state.explored.values()))
        best = None
        for freedom, state in game_state.explored.items():
            n = sum(state.outcome)
            cost = getattr(state.outcome, maximize) / n + math.sqrt(t / n)
            if best is None or best_cost < cost:
                best = state
                best_cost = cost
                best_freedom = freedom
        return best_freedom, best

