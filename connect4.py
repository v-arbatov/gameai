from mcts import RandomGameStrategy
from connect4_state import Connect4, Connect4GameState


def play_X(complexity = 5000):
    """Play for X, MCTS plays for O"""
    game_state = Connect4GameState(Connect4(token = Connect4.X))
    strategy = RandomGameStrategy(complexity)

    print(game_state.state)

    while True:
        token = game_state.state.token
        while True:
            column = int(input(token +'''. Which column do you want to place in?'''))
            if column in game_state.state.availableColumns():
                break
            print('''I'm sorry, but you can't place tokens in this column:''', column)

        game_state = game_state.getChildByColumn(column)
        print(game_state.state)
        if game_state.state.checkWin(column):
            print('Congratuations, {}! You won!'.format(token))
            break

        strategy.explore(game_state)
        game_state.print_choices()
        freedom, game_state = strategy.move(game_state)
        print(game_state.state)
        if game_state.terminal and game_state.outcome.losses > 0:
            print('Congratuations, O! You won!')
            break


def play_comp_comp(complexity = 1000):
    game_state = Connect4GameState(Connect4(token = Connect4.X))
    strategy = RandomGameStrategy(complexity)

    print(game_state.state)
    while True:
        for token in [Connect4.X, Connect4.O]:
            strategy.explore(game_state)
            game_state.print_choices()
            freedom, game_state = strategy.move(game_state)
            print(game_state.state)
            if game_state.terminal:
                if game_state.outcome.losses > 0:
                    print('Congratuations, {}! You won!'.format(token))
                    return token
                else:
                    print('DRAW!')
                    return 'DRAW'

def play_comp_comp_games(count = 100, complexity = 1000):
    stats = collections.defaultdict(int)

    for _ in range(count):
        stats[play_comp_comp(complexity)] += 1
        print('============ stats ===========', stats)

    print('DONE')
    print(stats)

##########################

play_X()
# play_comp_comp()

