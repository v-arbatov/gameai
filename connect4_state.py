import sys
import collections
import mcts

class Connect4:
    """Connect 4 Game State"""

    # Token symbols
    X = 'X'
    O = 'O'

    # Number of columns and rows on the board
    COLUMNS = 7
    ROWS = 6

    def __init__(self, token = 'X', board = collections.defaultdict(list)):
        # Player whos turn this is.
        self.token = token
        # Current game board: dictionary, map from column index to list of tokens from bottom to the top.
        self.board = board

    def availableColumns(self):
        """Returns list of column indices where current player can drop token"""
        return [i for i in range(self.COLUMNS) if len(self.board[i]) < self.ROWS]

    def dropToken(self, column):
        """Drops current token into <column> and returns new Connect4 instance with the new state"""
        # Check if column is full and return None if that is the case
        if len(self.board[column]) == self.ROWS:
            return None
        board = {c: [x for x in self.board[c]] for c in range(self.COLUMNS)}
        board[column].append(self.token)
        return Connect4(self.O if self.token == self.X else self.X, board)

    def checkWin(self, column):
        """ Returns True if the topmost token on the board in the <column> wins"""
        if self._countTokens(column,  0, -1) + self._countTokens(column,  0, 1) - 1 >= 4 \
           or self._countTokens(column, -1,  0) + self._countTokens(column,  1, 0) - 1 >= 4 \
           or self._countTokens(column,  1, -1) + self._countTokens(column, -1, 1) - 1 >= 4 \
           or self._countTokens(column, -1, -1) + self._countTokens(column,  1, 1) - 1 >= 4:
            return True
        return False

    def _countTokens(self, column, step_column, step_row):
        """Count tokens of the same kind in the specific direction from the tompost of the <column>"""
        row = len(self.board[column]) - 1
        token = self.board[column][row]
        line = 0
        for l in range(4):
            # check if leaving the board or hitting empty space or other token on the board
            if column < 0 or column >= self.COLUMNS \
               or row < 0 or row >= self.ROWS \
               or len(self.board[column]) <= row \
               or self.board[column][row] != token:
                break
            line += 1
            column += step_column
            row += step_row

        return line

    def __str__(self):
        result = []
        for row in range(self.ROWS):
            result.append(' '.join([self.board[x][row] if row < len(self.board[x]) else '.' for x in range(self.COLUMNS)]))
        result.append(' '.join([str(x) for x in range(self.COLUMNS)]))
        return '\n'.join(reversed(result))


class Connect4GameState(mcts.GameState):
    """Connect 4 game state for Monte Carlo Tree Search"""

    def __init__(self, state, terminal = False):
        super(Connect4GameState, self).__init__()
        self.state = state
        self.terminal = terminal or not self.state.availableColumns()
        if terminal:
            # Previous player WON, this layer LOST
            self.outcome = mcts.OUTCOME_LOSS
        elif self.terminal:
            # Previous player didn't end game but there are no more moves
            self.outcome = mcts.OUTCOME_DRAW

    def freedoms(self):
        # If game is complete there are no more moves
        if self.terminal:
            return 0
        return len(self.state.availableColumns())

    def _freedomToColumn(self, freedom):
        return self.state.availableColumns()[freedom]

    def _columnToFreedom(self, column):
        return self.state.availableColumns().index(column)

    def createChild(self, freedom):
        column = self._freedomToColumn(freedom)
        new_state = self.state.dropToken(column)
        return Connect4GameState(new_state, new_state.checkWin(column))

    def readChildOutcome(self, child):
        # Flip wins and losses because child is the opposite player
        wins, draws, losses = child.outcome
        return mcts.Outcome(wins = losses, draws = draws, losses = wins)

    def getChildByColumn(self, column):
        return self.getChildByFreedom(self._columnToFreedom(column))

    def print_choices(self, indent = 0):
        print(' '*indent + '====')
        for fr, ch in self.explored.items():
            column = self._freedomToColumn(fr)
            print(' '*indent, column, ':', ch.outcome)



