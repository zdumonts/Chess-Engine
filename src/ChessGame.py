import sys
import pygame
from ChessEngine import Move
from data.utils import load_image

# constants
SCREEN_WIDTH=600
SCREEN_HEIGHT=600
SQUARE_SIZE=75
IVORY = (255, 233, 197)
BEIGE = (100, 91, 77)
DEPTH = 5

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess Bot")
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.board = [['' for i in range(8)] for j in range(8)]
        self.clock = pygame.time.Clock()
        self.selSquare = ()
        self.playerClicks = []
        self.turn = 'white'
        self.moveLog = []

    def initialize(self):
        self.board[0] = ['black_rook', 'black_knight', 'black_bishop', 'black_queen', 
                        'black_king', 'black_bishop', 'black_knight', 'black_rook']
        self.board[1] = ['black_pawn']*8
        self.board[6] = ['white_pawn']*8
        self.board[7] = ['white_rook', 'white_knight', 'white_bishop', 'white_queen', 
                        'white_king', 'white_bishop', 'white_knight', 'white_rook']

    def running(self, engine):
        self.initialize()
        self.draw()
        while True: # game loop
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        location=pygame.mouse.get_pos()
                        startCol = location[0]//SQUARE_SIZE
                        startRow = location[1]//SQUARE_SIZE
                        self.selSquare = (startRow,startCol)
                        self.playerClicks.append(self.selSquare)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        location=pygame.mouse.get_pos()
                        endCol = location[0]//SQUARE_SIZE
                        endRow = location[1]//SQUARE_SIZE
                        self.selSquare = (endRow, endCol)
                        self.playerClicks.append(self.selSquare)
                        if len(self.playerClicks) == 2:
                            move = Move(self.playerClicks[0], self.playerClicks[1], self.board)
                            validMoves = self.validMoves()
                            if move in validMoves:
                                self.makeMove(move)
                                self.enPassantCapture(move)
                                self.pawnPromo(move)
                                self.checkCastle(move)
                            self.selSquare = ()
                            self.playerClicks = []
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

            if engine and self.turn == engine.color:
                move = engine.engineMove(DEPTH)
                self.makeMove(move)
                self.enPassantCapture(move)
                self.pawnPromo(move)
                self.checkCastle(move)
            
            if self.checkMate() or self.staleMate():
                self.gameOver(engine)
                sys.exit()

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)  

    def gameOver(self, engine):
        if self.staleMate():
            print("Draw!")
        elif self.turn == engine.color:
            print("You win!")
        else:
            print("You lose!")
        

    def checkCastle(self, move):
        # move rook to correct position
        if move:
            if 'king' in move.pieceMoved:
                if move.startRow == 0 and move.startCol == 4 and move.endRow == 0:
                    if move.endCol == 2:
                        self.board[0][0] = ''
                        self.board[0][3] = 'black_rook'
                    elif move.endCol == 6:
                        self.board[0][7] = ''
                        self.board[0][5] = 'black_rook'
                elif move.startRow == 7 and move.startCol == 4 and move.endRow == 7:
                    if move.endCol == 2:
                        self.board[7][0] = ''
                        self.board[7][3] = 'white_rook'
                    elif move.endCol == 6:
                        self.board[7][7] = ''
                        self.board[7][5] = 'white_rook'
    
    def castling(self, moves):
        # castling_rights (black_king to rook at 0,0 , black_king to rook at 0,7 ,
        #                  white_king to rook at 7,0 , white_king to rook at 7, 7)
        castling_rights = [True, True, True, True]
        for move in self.moveLog:
            if castling_rights == (False, False, False, False):
                break
            elif move.pieceMoved == 'black_king':
                castling_rights[0], castling_rights[1] = False, False
            elif move.pieceMoved == 'white_king':
                castling_rights[2], castling_rights[3] = False, False
            elif 'rook' in move.pieceMoved:
                if move.startRow == 0 and move.startCol == 0:
                    castling_rights[0] = False
                elif move.startRow == 0 and move.startCol == 7:
                    castling_rights[1] = False
                elif move.startRow == 7 and move.startCol == 0:
                    castling_rights[2] = False
                elif move.startRow == 7 and move.startCol == 7:
                    castling_rights[3] = False
        if castling_rights[0] == True:
            if (not self.isAttacked(0,1) and not self.isAttacked(0,2) and not self.isAttacked(0,3) and 
                not self.isAttacked(0,4) and not self.board[0][3] and not self.board[0][1] and not self.board[0][2]):
                moves.append(Move((0,4),(0,2), self.board))
        if castling_rights[1] == True:
            if (not self.isAttacked(0,6) and not self.isAttacked(0,5) and not self.isAttacked(0,4) and 
                not self.board[0][6] and not self.board[0][5]):
                moves.append(Move((0,4),(0,6), self.board))
        if castling_rights[2] == True:
            if (not self.isAttacked(7,1) and not self.isAttacked(7,2) and not self.isAttacked(7,3) and 
                not self.isAttacked(7,4) and not self.board[7][3] and not self.board[7][1] and not self.board[7][2]):
                moves.append(Move((7,4),(7,2), self.board))
        if castling_rights[3] == True:
            if (not self.isAttacked(7,6) and not self.isAttacked(7,5) and not self.isAttacked(7,4) and 
                not self.board[7][6] and not self.board[7][5]):
                moves.append(Move((7,4),(7,6), self.board))
        return moves
    
    def enPassant(self, moves):
        if not self.moveLog:
            return moves
        move = self.moveLog[len(self.moveLog)-1]
        if 'white_pawn' == move.pieceMoved and move.startRow == 6 and move.endRow == 4:
            if move.endCol < 7 and self.board[move.endRow][move.endCol+1] == 'black_pawn':
                moves.append(Move((4, move.endCol+1), (5, move.endCol), self.board))
            elif move.endCol > 0 and self.board[move.endRow][move.endCol-1] == 'black_pawn':
                moves.append(Move((4, move.endCol-1), (5, move.endCol), self.board))
        elif 'black_pawn' == move.pieceMoved and move.startRow == 1 and move.endRow == 3:
            if move.endCol < 7 and self.board[3][move.endCol+1] == 'white_pawn':
                moves.append(Move((3, move.endCol+1), (2, move.endCol), self.board))
            elif move.endCol > 0 and self.board[3][move.endCol-1] == 'white_pawn':
                moves.append(Move((3, move.endCol-1), (2, move.endCol), self.board))
        return moves
    
    def enPassantCapture(self, move):
        if move:
            color = self.color(move.endRow, move.endCol)
            if 'pawn' in self.board[move.endRow][move.endCol] and move.startCol != move.endCol and not move.pieceCaptured:
                if color == 'black':
                    self.board[move.endRow-1][move.endCol] = ''
                    move.pieceCaptured = 'whtie_pawn'
                self.board[move.endRow+1][move.endCol] = ''
                move.pieceCaptured = 'black_pawn'

    def checkMate(self):
        moves = self.validMoves()
        if not moves and self.check():
            return True
        return False
    
    def staleMate(self):
        moves = self.validMoves()
        if not moves and not self.check():
            return True
        return False

    def makeMove(self, move):
        if move:
            self.board[move.startRow][move.startCol] = ""
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.turn = 'black' if self.turn == 'white' else 'white'
            self.moveLog.append(move)

    def pawnPromo(self, move):
        if move:
            if 'pawn' in self.board[move.endRow][move.endCol] and (move.endRow == 0 or move.endRow == 7):
                promoInput = ''
                while not promoInput:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                promoInput = 'queen'
                            elif event.key == pygame.K_r:
                                promoInput = 'rook'
                            elif event.key == pygame.K_k:
                                promoInput = 'knight'
                            elif event.key == pygame.K_b:
                                promoInput = 'bishop'
                if move.endRow == 0:
                    self.board[move.endRow][move.endCol] = f'white_{promoInput}'
                else:
                    self.board[move.endRow][move.endCol] = f'black_{promoInput}'

    def isAttacked(self, row, col):
        self.turn = 'white' if self.turn == 'black' else 'black'
        oppMoves = self.allMoves()
        self.turn = 'white' if self.turn == 'black' else 'black'
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False  

    def check(self):
        if self.turn == 'white':
            return self.isAttacked(self.getLocation('white_king')[0], self.getLocation('white_king')[1])
        else:
            return self.isAttacked(self.getLocation('black_king')[0], self.getLocation('black_king')[1])

    def validMoves(self):
        moves = self.allMoves()
        moves = self.enPassant(moves)
        moves = self.castling(moves)
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.turn = 'white' if self.turn == 'black' else 'black'
            if self.check():
                moves.remove(moves[i])
            self.turn = 'white' if self.turn == 'black' else 'black'
            self.undoMove()
        return moves
    
    def undoMove(self):
        if self.moveLog:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.turn = 'white' if self.turn == 'black' else 'black'

    def allMoves(self):
        moves=[]
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and self.color(row,col) == self.turn:
                    if 'pawn' in piece:
                        self.pawnMoves(row, col, moves)
                    elif 'rook' in piece:
                        self.rookMoves(row, col, moves)
                    elif 'knight' in piece:
                        self.knightMoves(row, col, moves)
                    elif 'bishop' in piece:
                        self.bishopMoves(row, col, moves)
                    elif 'queen' in piece:
                        self.rookMoves(row, col, moves)
                        self.bishopMoves(row, col, moves)
                    elif 'king' in piece:
                        self.kingMoves(row, col, moves)
        return moves
    
    def kingMoves(self, row, col, moves):
        if self.color(row,col) == self.turn:
            # up
            if row > 0 and not self.board[row-1][col]:
                moves.append(Move((row, col), (row-1, col), self.board))
            elif row > 0 and self.color(row, col) != self.color(row-1, col):
                moves.append(Move((row, col), (row-1, col), self.board))
            # upright
            if row > 0 and col < 7 and not self.board[row-1][col+1]:
                moves.append(Move((row, col), (row-1, col+1), self.board))
            elif row > 0 and col < 7 and self.color(row, col) != self.color(row-1, col+1):
                moves.append(Move((row, col), (row-1, col+1), self.board))
            # upleft
            if row > 0 and col > 0 and not self.board[row-1][col-1]:
                moves.append(Move((row, col), (row-1, col-1), self.board))
            elif row > 0 and col > 0 and self.color(row, col) != self.color(row-1, col-1):
                moves.append(Move((row, col), (row-1, col-1), self.board))
            # right
            if col < 7 and not self.board[row][col+1]:
                moves.append(Move((row, col), (row, col+1), self.board))
            elif col < 7 and self.color(row, col) != self.color(row, col+1):
                moves.append(Move((row, col), (row, col+1), self.board))
            # left
            if col > 0 and not self.board[row][col-1]:
                moves.append(Move((row, col), (row, col-1), self.board))
            elif col > 0 and self.color(row, col) != self.color(row, col-1):
                moves.append(Move((row, col), (row, col-1), self.board))
            # downright
            if row < 7 and col < 7 and not self.board[row+1][col+1]:
                moves.append(Move((row, col), (row+1, col+1), self.board))
            elif row < 7 and col < 7 and self.color(row, col) != self.color(row+1, col+1):
                moves.append(Move((row, col), (row+1, col+1), self.board))
            # downleft
            if row < 7 and col > 0 and not self.board[row+1][col-1]:
                moves.append(Move((row, col), (row+1, col-1), self.board))
            elif row < 7 and col > 0 and self.color(row, col) != self.color(row+1, col-1):
                moves.append(Move((row, col), (row+1, col-1), self.board))
            # down
            if row < 7 and not self.board[row+1][col]:
                moves.append(Move((row, col), (row+1, col), self.board))
            elif row < 7 and self.color(row, col) != self.color(row+1, col):
                moves.append(Move((row, col), (row+1, col), self.board))
        return moves 

    
    def pawnMoves(self, row, col, moves):
        if self.turn == 'white':
            # white pawn move
            if not self.board[row-1][col]:
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and not self.board[4][col]:
                    moves.append(Move((6,col), (4, col), self.board))
            # white pawn capture 
            if col > 0 and "black" in self.board[row-1][col-1]:
                moves.append(Move((row, col), (row-1, col-1), self.board))
            if col < 7 and "black" in self.board[row-1][col+1]:
                moves.append(Move((row, col), (row-1, col+1), self.board))
        else:
            # black pawn move
            if not self.board[row+1][col]:
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and not self.board[3][col]:
                    moves.append(Move((1, col), (3, col), self.board))
            # black pawn capture
            if col > 0 and "white" in self.board[row+1][col-1]:
                moves.append(Move((row, col), (row+1, col-1), self.board))
            if col < 7 and "white" in self.board[row+1][col+1]:
                moves.append(Move((row, col), (row+1, col+1), self.board))
        return moves
    
    def rookMoves(self, row, col, moves):
        if self.color(row,col) == self.turn:
            # up
            for i in range(row+1,8):
                    if not self.board[i][col]:
                        moves.append(Move((row, col),(i, col), self.board))
                        continue
                    elif self.color(row,col) != self.color(i,col):
                        moves.append(Move((row, col), (i, col), self.board))
                    break
            # down
            for i in range(row-1, -1, -1):
                if not self.board[i][col]:
                    moves.append(Move((row, col),(i, col), self.board))
                    continue
                elif self.color(row,col) != self.color(i,col):
                    moves.append(Move((row, col), (i, col), self.board))
                break
            # right 
            for i in range(col+1,8):
                if not self.board[row][i]:
                    moves.append(Move((row, col),(row, i), self.board))
                    continue
                elif self.color(row,col) != self.color(row,i):
                    moves.append(Move((row, col), (row, i), self.board))
                break
            # left
            for i in range(col-1, -1, -1):
                if not self.board[row][i]:
                    moves.append(Move((row, col),(row, i), self.board))
                    continue
                elif self.color(row,col) != self.color(row,i):
                    moves.append(Move((row, col), (row, i), self.board))
                break 
        return moves  

    def knightMoves(self, row, col, moves):
        if self.color(row,col) == self.turn:
            # upright
            if row > 1 and col < 7 and not self.board[row-2][col+1]:
                moves.append(Move((row, col), (row-2, col+1), self.board))
            elif row > 1 and col < 7 and self.color(row, col) != self.color(row-2, col+1):
                moves.append(Move((row, col), (row-2, col+1), self.board))
            # upleft
            if row > 1 and col > 0 and not self.board[row-2][col-1]:
                moves.append(Move((row, col), (row-2, col-1), self.board))
            elif row > 1 and col > 0 and self.color(row, col) != self.color(row-2, col-1):
                moves.append(Move((row, col), (row-2, col-1), self.board))
            # rightup
            if row > 0 and col < 6 and not self.board[row-1][col+2]:
                moves.append(Move((row, col), (row-1, col+2), self.board))
            elif row > 0 and col < 6 and self.color(row, col) != self.color(row-1, col+2):
                moves.append(Move((row, col), (row-1, col+2), self.board))
            # rightdown
            if row < 7 and col < 6 and not self.board[row+1][col+2]:
                moves.append(Move((row, col), (row+1, col+2), self.board))
            elif row < 7 and col < 6 and self.color(row, col) != self.color(row+1, col+2):
                moves.append(Move((row, col), (row+1, col+2), self.board))
            # leftup
            if row > 0 and col > 1 and not self.board[row-1][col-2]:
                moves.append(Move((row, col), (row-1, col-2), self.board))
            elif row  > 0 and col > 1 and self.color(row, col) != self.color(row-1, col-2):
                moves.append(Move((row, col), (row-1, col-2), self.board))
            # leftdown
            if row < 7 and col > 1 and not self.board[row+1][col-2]:
                moves.append(Move((row, col), (row+1, col-2), self.board))
            elif row < 7 and col > 1 and self.color(row, col) != self.color(row+1, col-2):
                moves.append(Move((row, col), (row+1, col-2), self.board))
            # downleft
            if row < 6 and col > 0 and not self.board[row+2][col-1]:
                moves.append(Move((row, col), (row+2, col-1), self.board))
            elif row < 6 and col > 0 and self.color(row, col) != self.color(row+2, col-1):
                moves.append(Move((row, col), (row+2, col-1), self.board))
            # downright
            if row < 6 and col < 7 and not self.board[row+2][col+1]:
                moves.append(Move((row, col), (row+2, col+1), self.board))
            elif row < 6 and col < 7 and self.color(row, col) != self.color(row+2, col+1):
                moves.append(Move((row, col), (row+2, col+1), self.board))
        return moves 
        
    
    def bishopMoves(self, row, col, moves):
        if self.color(row,col) == self.turn:
            # downright
            count = 1
            for i in range(row+1,8):
                if col + count <= 7 and not self.board[i][col+count]:
                    moves.append(Move((row, col), (i, col+count), self.board))
                    count+=1
                    continue
                elif col + count <= 7 and self.color(row, col) != self.color(i, col+count):
                    moves.append(Move((row, col), (i, col+count), self.board))
                break
            # downleft
            count = 1
            for i in range(row+1,8):
                if col - count >= 0 and not self.board[i][col-count]:
                    moves.append(Move((row, col), (i, col-count), self.board))
                    count+=1
                    continue
                elif col - count >= 0 and self.color(row, col) != self.color(i, col-count):
                    moves.append(Move((row, col), (i, col-count), self.board))
                break
            # upright
            count = 1
            for i in range(row-1,-1,-1):
                if col + count <= 7 and not self.board[i][col+count]:
                    moves.append(Move((row, col), (i, col+count), self.board))
                    count+=1
                    continue
                elif col + count <= 7 and self.color(row, col) != self.color(i, col+count):
                    moves.append(Move((row, col), (i, col+count), self.board))
                break
            # upleft
            count = 1
            for i in range(row-1,-1,-1):
                if col - count >= 0 and not self.board[i][col-count]:
                    moves.append(Move((row, col), (i, col-count), self.board))
                    count+=1
                    continue
                elif col - count >= 0 and self.color(row, col) != self.color(i, col-count):
                    moves.append(Move((row, col), (i, col-count), self.board))
                break
        return moves

    def getLocation(self, piece):
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == piece:
                    return (row, col)
        return "not found"

    def color(self, row, col):
        piece = self.board[row][col]
        color = 'black' if 'black' in piece else 'white'
        return color

    def draw(self):
        # draw board
        count = 0
        for x in range(0, SCREEN_WIDTH, SQUARE_SIZE):
            for y in range(0, SCREEN_HEIGHT, SQUARE_SIZE):
                color = BEIGE if count % 2 == 0 else IVORY
                rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                count+=1
            count+=1

        #draw pieces
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    self.screen.blit(load_image(piece+".png"), (col*SQUARE_SIZE,row*SQUARE_SIZE))