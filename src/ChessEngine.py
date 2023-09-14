import random
import math

class Move():
    def __init__(self, startSquare, endSquare, board):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        
    def __eq__(self, other):
        if self.moveID == other.moveID:
            return True
        return False
    
    def __str__(self):
        return str(self.moveID)

class Engine(): # minimax
    def __init__(self, color, game):
        self.color = color
        self.game = game
        self.pieceValues = {'white_pawn':1, 'black_pawn':1, 'white_knight':3, 'black_knight':3, 
                            'white_bishop':3, 'black_bishop':3, 'white_rook':5, 'black_rook':5,
                            'white_queen': 8, 'black_queen': 8, 'white_king':0, 'black_king':0}
        self.engineMoveLog = []

    def randomMove(self):
        # choose a random move in valid moves
        rand = random.randint(0, len(self.game.validMoves())-1)
        move = self.game.validMoves()[rand]
        return move

    def engineMove(self, depth):
        if self.game.validMoves():
            bestMove = self.game.validMoves()[0] # set best move to first move
            alpha = -math.inf
            beta = math.inf
            validMoves = self.newValidMoves(self.game.validMoves())
            for move in validMoves:
                self.game.makeMove(move)
                value = self.minimax(depth-1, alpha, beta, False)
                self.game.undoMove()
                if value > alpha:
                    alpha = value
                    bestMove = move
            return bestMove

    def minimax(self, depth, alpha, beta, maximizingPlayer):
        if depth == 0: # base case
            return self.scoreEval()
        if maximizingPlayer: # recursive call
            best_value = -math.inf
            validMoves = self.newValidMoves(self.game.validMoves())
            for move in validMoves:
                self.game.makeMove(move)
                value = self.minimax(depth-1, alpha, beta, False)
                self.game.undoMove()
                best_value = max(value, best_value)
                alpha = max(value, alpha)
                if beta <= alpha:
                    break
            return best_value
        else:
            best_value = math.inf
            validMoves = self.newValidMoves(self.game.validMoves())
            for move in validMoves:
                self.game.makeMove(move)
                value = self.minimax(depth-1, alpha, beta, True)
                self.game.undoMove()
                best_value = min(value, best_value)
                beta = min(value, beta)
                if beta <= alpha:
                    break
            return best_value
  
    def scoreEval(self):
        score = 0
        for row in range(8):
            for col in range(8):
                if self.color in self.game.board[row][col]:
                    score+=self.pieceValues[self.game.board[row][col]]
                elif self.game.board[row][col]:
                    score-=self.pieceValues[self.game.board[row][col]]
        return score
    
    def newValidMoves(self, validMoves):
        # order best moves to front of list or better alpha beta pruning
        newMoves = []
        temp = []
        for move in validMoves:
            if move.pieceCaptured:
                if self.pieceValues[move.pieceMoved] > self.pieceValues[move.pieceMoved]:
                    newMoves.append(move)
                else:
                    newMoves.append(move)
            else:
                temp.append(move)
        newMoves+=temp
        return newMoves          