from ChessGame import Game
from ChessEngine import Engine

if __name__ == '__main__':
    # initialize AI
    game = Game()
    engine = Engine('black', game)
    game.running(engine)
    