import random
import time
import copy
import sys
import pisqpipe as pp
import math
from pisqpipe import DEBUG_EVAL, DEBUG
sys.setrecursionlimit(100)

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
adjacent = []  


def check_board(board):
    for i in range(MAX_BOARD):
        for j in range(MAX_BOARD):
            if isFree(i,j) != 1:
                return False
    return True

def isCrossing(x, y):
    return x < 0 or y < 0 or x >= pp.width or y >= pp.height

def oppsite_who(who):
    if who == 1:
        return 2
    if who == 2:
        return 1

def check_win(board, x, y, who):
    left = 0
    right = 0
    while x-left-1 >= 0 and board[x-left-1][y] == who:
        left += 1
    while x+right+1 < MAX_BOARD and board[x+right+1][y] == who:
        right += 1
    if right + left + 1 >= 5:
        return True
    down = 0
    up = 0
    while y-down-1 >= 0 and board[x][y-down-1] == who:
        down += 1
    while y+up+1 < MAX_BOARD and board[x][y+up+1] == who:
        up += 1
    if up + down + 1 >= 5:
        return True
    upperLeft = 0
    lowerRight = 0
    while x-upperLeft-1 >= 0 and y+upperLeft+1 < MAX_BOARD and board[x-upperLeft-1][y+upperLeft+1] == who:
        upperLeft += 1
    while x+lowerRight+1 < MAX_BOARD and y-lowerRight-1 >= 0 and board[x+lowerRight+1][y-lowerRight-1] == who:
        lowerRight += 1
    if lowerRight + upperLeft + 1 >= 5:
        return True


    lowerLeft = 0
    upperRight = 0
    while x-lowerLeft-1 >= 0 and y-lowerLeft-1 >= 0 and board[x-lowerLeft-1][y-lowerLeft-1] == who:
        lowerLeft += 1
    while x+upperRight+1 < MAX_BOARD and y+upperRight+1 < MAX_BOARD and board[x+upperRight+1][y+upperRight+1] == who:
        upperRight += 1
    if upperRight + lowerLeft + 1 >= 5:
        return True
    
    return False
          

def my_heuristic(board, x, y, who):
    heuristic = 0.0
    factor = 0.85
    left = 0
    right = 0
    row_opponent = 0

    if x-left-1 < 0:
        row_opponent += 1

    while x-left-1 >= 0:
        if board[x-left-1][y] == who:
            left += 1
            if x-left-1 < 0:
                row_opponent += 1
                break
        elif board[x-left-1][y] == oppsite_who(who):
            row_opponent += 1
            break
        elif board[x-left-1][y] == 0:
            break        
    if x+right+1 >= MAX_BOARD:
        row_opponent += 1
    while x+right+1 < MAX_BOARD:
        if board[x+right+1][y] == who:
            right += 1
            if x+right+1 >= MAX_BOARD:
                row_opponent += 1
                break
        elif board[x+right+1][y] == oppsite_who(who):
            row_opponent += 1
            break
        elif board[x+right+1][y] == 0:
            break  

    if right + left >= 4:
        heuristic += 1000000
    else:
        if row_opponent == 0 and right + left > 0:
            heuristic += 10 ** (left + right + 1.0)
        elif row_opponent == 1 and right + left > 0:
            heuristic += 10 ** (left + right)
        elif row_opponent == 2:
            heuristic += 0
    down = 0
    up = 0
    col_opponent = 0
    if y-down-1 < 0:
        col_opponent += 1
    while y-down-1 >= 0:
        if board[x][y-down-1] == who:
            down += 1
            if y-down-1 < 0:
                col_opponent += 1
                break
        elif board[x][y-down-1] == oppsite_who(who):
            col_opponent += 1
            break
        elif board[x][y-down-1] == 0:
            break        
    if y+up+1 >= MAX_BOARD:
        col_opponent += 1
    while y+up+1 < MAX_BOARD:
        if board[x][y+up+1] == who:
            up += 1
            if y+up+1 >= MAX_BOARD:
                col_opponent += 1
                break 
        elif board[x][y+up+1] == oppsite_who(who):
            col_opponent += 1
            break
        elif board[x][y+up+1] == 0:
            break
    if up + down >= 4:
        heuristic += 10 ** 5
    else:
        if col_opponent == 0 and up + down > 0:
            heuristic += 10 ** (up + down + 1.0)
        elif col_opponent == 1 and up + down > 0:
            heuristic += 10 ** (up + down)
        elif col_opponent == 2:
            heuristic += 0 
    upperLeft = 0
    lowerRight = 0
    diag1_opponent = 0
    if x-upperLeft-1 < 0 or y+upperLeft+1 >= MAX_BOARD:
        diag1_opponent += 1
    while x-upperLeft-1 >= 0 and y+upperLeft+1 < MAX_BOARD:
        if board[x-upperLeft-1][y+upperLeft+1] == who:
            upperLeft += 1
            if x-upperLeft-1 < 0 or y+upperLeft+1 >= MAX_BOARD:
                diag1_opponent += 1
                break
        elif board[x-upperLeft-1][y+upperLeft+1] == oppsite_who(who):
            diag1_opponent += 1
            break
        elif board[x-upperLeft-1][y+upperLeft+1] == 0:
            break        
    if x+lowerRight+1 >= MAX_BOARD or y-lowerRight-1 < 0:
        diag1_opponent += 1
    while x+lowerRight+1 < MAX_BOARD and y-lowerRight-1 >= 0:
        if board[x+lowerRight+1][y-lowerRight-1] == who:
            lowerRight += 1
            if x+lowerRight+1 >= MAX_BOARD or y-lowerRight-1 < 0:
                diag1_opponent += 1
                break
        elif board[x+lowerRight+1][y-lowerRight-1] == oppsite_who(who):
            diag1_opponent += 1
            break
        elif board[x+lowerRight+1][y-lowerRight-1] == 0:
            break
    if lowerRight + upperLeft >= 4:
        heuristic += 10 ** 5
    else:
        if diag1_opponent == 0 and lowerRight + upperLeft > 0:
            heuristic += 10 ** (lowerRight + upperLeft + 1.0)
        elif diag1_opponent == 1 and lowerRight + upperLeft > 0:
            heuristic += 10 ** (lowerRight + upperLeft)
        elif diag1_opponent == 2:
            heuristic += 0
    lowerLeft = 0
    upperRight = 0
    diag2_opponent = 0
    if x-lowerLeft-1 < 0 or y-lowerLeft-1 < 0:
        diag2_opponent += 1
    while x-lowerLeft-1 >= 0 and y-lowerLeft-1 >= 0:
        if board[x-lowerLeft-1][y-lowerLeft-1] == who:
            lowerLeft += 1
            if x-lowerLeft-1 < 0 or y-lowerLeft-1 < 0:
                diag2_opponent += 1
                break
        elif board[x-lowerLeft-1][y-lowerLeft-1] == oppsite_who(who):
            diag2_opponent += 1
            break
        elif board[x-lowerLeft-1][y-lowerLeft-1] == 0:
            break        
    if x+upperRight+1 >= MAX_BOARD or y+upperRight+1 >= MAX_BOARD:
        diag2_opponent += 1
    while x+upperRight+1 < MAX_BOARD and y+upperRight+1 < MAX_BOARD:
        if board[x+upperRight+1][y+upperRight+1] == who:
            upperRight += 1
            if x+upperRight+1 >= MAX_BOARD or y+upperRight+1 >= MAX_BOARD:
                diag2_opponent += 1
                break
        elif board[x+upperRight+1][y+upperRight+1] == oppsite_who(who):
            diag2_opponent += 1
            break
        elif board[x+upperRight+1][y+upperRight+1] == 0:
            break 
    if upperRight + lowerLeft >= 4:
        heuristic += 10 ** 5
    else:
        if diag2_opponent == 0 and upperRight + lowerLeft > 0:
            heuristic += 10 ** (upperRight + lowerLeft + 1.0) 
        elif diag2_opponent == 1 and upperRight + lowerLeft > 0:
            heuristic += 10 ** (upperRight + lowerLeft)
        elif diag2_opponent == 2:
            heuristic += 0
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if i == 0 and j == 0:
                continue
            if isCrossing(x+3*i, y+3*j) != 1 and isCrossing(x-2*i, y-2*j) != 1:
                if board[x-1*i][y-1*j] == who and board[x-2*i][y-2*j] == 0 and board[x+1*i][y+1*j] == 0 and  board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == 0:
                    heuristic += 1000 * factor - 100
            if isCrossing(x+4*i, y+4*j) != 1 and isCrossing(x-1*i, y-1*j) != 1:
                if board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == 0:
                    heuristic += 1000 * factor
                elif board[x+1*i][y+1*j] == who and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == 0:
                    heuristic += 1000 * factor - 100
            if isCrossing(x+3*i, y+3*j) != 1 and isCrossing(x-2*i, y-2*j) != 1:
                if board[x+1*i][y+1*j] == 0 and board[x-1*i][y-1*j] == who and board[x-2*i][y-2*j] == oppsite_who(who) and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == 0:
                    heuristic += 50 * factor * factor - 10
            if isCrossing(x+4*i, y+4*j) != 1 and isCrossing(x-1*i, y-1*j) != 1:
                if board[x+1*i][y+1*j] == who and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+4*i][y+4*j] == 0:
                    heuristic += 50 * factor * factor - 10
                elif board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == oppsite_who(who):
                    heuristic += 50 * factor * factor
                elif board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == oppsite_who(who) and board[x+4*i][y+4*j] == 0:
                    heuristic += 50 * factor * factor
                elif board[x+1*i][y+1*j] == who and board[x+2*i][y+2*j] == 0 and board[x+3*i][y+3*j] == who and board[x-1*i][y-1*j] == 0 and board[x+4*i][y+4*j] == oppsite_who(who):
                    heuristic += 50 * factor * factor
            if isCrossing(x+2*i, y+2*j) != 1 and isCrossing(x-3*i, y-3*j) != 1:
                if board[x+1*i][y+1*j] == who and board[x-1*i][y-1*j] == 0 and board[x-2*i][y-2*j] == who and board[x+2*i][y+2*j] == 0 and board[x-3*i][y-3*j] == oppsite_who(who):
                    heuristic += 50 * factor * factor
            if isCrossing(x-5*i, y-5*j) != 1:
                if board[x-1*i][y-1*j] == 0  and board[x-2*i][y-2*j] == who and board[x-3*i][y-3*j] == who and board[x-4*i][y-4*j] == who and board[x-5*i][y-5*j] == oppsite_who(who):
                    heuristic += 20000 * factor * factor - 10 
                elif board[x-1*i][y-1*j] == who  and board[x-2*i][y-2*j] == 0 and board[x-3*i][y-3*j] == who and board[x-4*i][y-4*j] == who and board[x-5*i][y-5*j] == oppsite_who(who):
                    heuristic += 20000 * factor * factor - 100
            if isCrossing(x+1*i, y+1*j) != 1 and isCrossing(x-4*i, y-4*j) != 1:
                if board[x-1*i][y-1*j] == 0  and board[x-2*i][y-2*j] == who and board[x-3*i][y-3*j] == who and board[x-4*i][y-4*j] == oppsite_who(who) and board[x+1*i][y+1*j] == who:
                    heuristic += 20000 * factor * factor - 100
            if isCrossing(x-3*i, y-3*j) != 1 and isCrossing(x+3*i, y+3*j) != 1:
                if board[x-3*i][y-3*j] == 0 and board[x-2*i][y-2*j] == who and board[x-1*i][y-1*j] == 0 and board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == 0:
                    heuristic += 200 * factor * factor * factor
            if isCrossing(x-1*i, y-1*j) != 1 and isCrossing(x+3*i, y+3*j) != 1:
                if board[x-1*i][y-1*j] == 0 and board[x+1*i][y+1*j] == 0 and board[x+2*i][y+2*j] == who and board[x+3*i][y+3*j] == 0:
                    heuristic += 5 * factor * factor
    
    if isCrossing(x + 1,y + 2) != 1 and board[x+1][y+2] == who:
        heuristic += 10
    if isCrossing(x - 1,y + 2) != 1 and board[x-1][y+2] == who:
        heuristic += 10
    if isCrossing(x + 1,y - 2) != 1 and board[x+1][y-2] == who:
        heuristic += 10
    if isCrossing(x - 1,y - 2) != 1 and board[x-1][y-2] == who:
        heuristic += 10
    if isCrossing(x + 2,y + 1) != 1 and board[x+2][y+1] == who:
        heuristic += 10
    if isCrossing(x + 2,y - 1) != 1 and board[x+2][y-1] == who:
        heuristic += 10
    if isCrossing(x - 2,y + 1) != 1 and board[x-2][y+1] == who:
        heuristic += 10
    if isCrossing(x - 2,y - 1) != 1 and board[x-2][y-1] == who:
        heuristic += 10

    return heuristic

def confront_heuristic(board, x, y, who): 
    beta = 1/6   
    return beta * my_heuristic(board, x, y, who) + (1-beta) * my_heuristic(board, x, y, oppsite_who(who))/10

def Adjacent(board):
    adjacent = []
    for x in range(MAX_BOARD):
        for y in range(MAX_BOARD):
            if isFree(x, y):
                tag = 0
                for i in range(-2, 3, 1):
                    for j in range(-2, 3, 1):
                        if isCrossing(x+i,y+j):
                            continue
                        if isFree(x+i,y+j):
                            continue
                        else:
                            tag = 1
                if tag == 1:
                    adjacent.append((x,y))                        
    return adjacent

def Adjacent_1(board, old_adjacent, x, y):  
    adjacent = []
    adjacent = old_adjacent
    adjacent.remove((x,y))
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            if isFree(x+i,y+j):
                if isCrossing(x+i,y+j):
                    continue
                if (x+i,y+j) in adjacent:
                    continue
                else:
                    adjacent.append((x+i,y+j))
            else:
                continue                           
    return adjacent

def Adjacent_2(board, old_adjacent, x, y): 
    adjacent = []
    adjacent = old_adjacent
    adjacent.remove((x,y))
    for i in range(-2, 3, 1):
        for j in range(-2, 3, 1):
            if isFree(x+i,y+j):
                if isCrossing(x+i,y+j):
                    continue
                if (x+i,y+j) in adjacent:
                    continue
                else:
                    adjacent.append((x+i,y+j))
            else:
                continue                           
    return adjacent

def Pruning_Adjacent(board, adjacent, who): 
    Pruning_Adjacent = []
    score = {}
    for (x,y) in adjacent:
        score[(x,y)] = confront_heuristic(board, x, y, who)
    rank = sorted(score.items(), key = lambda item:item[1], reverse = True)
    for i in range(0, 4):
        Pruning_Adjacent.append(rank[i][0])
    return Pruning_Adjacent

def Simulate_Pruning_Adjacent(board, adjacent, who):   
    Pruning_Adjacent = []
    score = {}
    for (x,y) in adjacent:
        score[(x,y)] = confront_heuristic(board, x, y, who)
    rank = sorted(score.items(), key = lambda item:item[1], reverse = True)
    for i in range(0, 2):
        Pruning_Adjacent.append(rank[i][0])
    return Pruning_Adjacent

class MCTS_UCT(object):

    def __init__(self, board, play_turn, time=10, max_actions=100):
 
        self.board = board
        self.play_turn = play_turn   
        self.calculation_time = float(time-0.6)   
        self.max_actions = max_actions   
        self.board_availables = Adjacent(board)  
        self.confident = 1.414
        self.plays = {}  
        self.wins = {}   
        self.max_depth = 1

    def get_action(self): 
        self.plays = {} 
        self.wins = {}
        simulations = 0
        for x, y in self.board_availables:
            if check_win(board, x, y, 1):
                return (x, y)
        for x, y in self.board_availables:
            if check_win(board, x, y, 2):
                return (x, y)
        
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            board_copy = copy.deepcopy(self.board)   
            play_turn_copy = copy.deepcopy(self.play_turn)    
            self.run_simulation(board_copy, play_turn_copy)    
            simulations += 1                          
        move = self.select_one_move() 
        return move

    def select_one_move(self):
        data= {}
        availables = Pruning_Adjacent(board, self.board_availables, 1)
        for move in availables:  
            data[move] = (self.wins.get((1, move), 0) /
            self.plays.get((1, move), 1)) + confront_heuristic(board, move[0], move[1], 1)/1000   
        move, percent_wins = sorted(data.items(), key = lambda item:item[1], reverse = True)[0] 
        return move

    def get_player(self, players):  
        p = players.pop(0)
        players.append(p)
        return p
    
    def run_simulation(self, board, play_turn):
        plays = self.plays
        wins = self.wins
        adjacent = self.board_availables   
        player = self.get_player(play_turn) 
        visited_states = set() 
        winner = -1
        expand = True
        availables = Pruning_Adjacent(board, adjacent, player)
        for t in range(1, self.max_actions + 1):
            tag = 0
            for (x,y) in adjacent:
                if check_win(board, x, y, player):
                    move = (x,y)
                    tag = 1
                    break
            for (x,y) in adjacent:
                if check_win(board, x, y, oppsite_who(player)):
                    move = (x,y)
                    tag = 1
                    break
            if tag == 0:              
                if player == 1:             
                    if all(plays.get((player, move)) for move in availables):
                        log_total = math.log(sum(plays[(player, move)] for move in availables))            
                        value, move = max(
                            (((wins[(player, move)] / plays[(player, move)]) +
                            math.sqrt(self.confident * log_total / plays[(player, move)])) + confront_heuristic(board, move[0], move[1], player)/1000, move) 
                            for move in availables)
                    else:
                        peripherals = []
                        for move in availables:
                            if not plays.get((player, move)):
                                peripherals.append(move)
                        move = random.sample(availables, int(len(peripherals)))[0]
                elif player == 2:
                    value, move = max(
                        (my_heuristic(board, move[0], move[1], player), move) 
                        for move in availables)
            board[move[0]][move[1]] = player   
            adjacent = Adjacent_1(board, adjacent, move[0], move[1])
            if expand and (player, move) not in plays:
                expand = False
                plays[(player, move)] = 0
                wins[(player, move)] = 0
                if t > self.max_depth:
                    self.max_depth = t
 
            visited_states.add((player, move))
            if check_win(board, move[0], move[1], player):
                winner = player
                break
            player = self.get_player(play_turn)
            availables = Simulate_Pruning_Adjacent(board, adjacent, player)
        
        last_x = move[0]
        last_y = move[1]   

        for player, move in visited_states:
            if (player, move) not in plays:
                continue
            plays[(player, move)] += 1 
            if player == winner:
                wins[(player, move)] += 1 
            elif winner == -1:
                wins[(player, move)] += 0.5    
            elif winner != player and winner != -1:
                wins[(player, move)] += 0.0
 
    def __str__(self):
        return "GUAGUAGUAGUA-AI"

def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")

def brain_restart():
    global adjacent
    adjacent = []
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	if isFree(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		board[x][y] = 0
		return 0
	return 2

def brain_turn():
    try:
        if pp.terminateAI:
            return
        i = 0
        while True:
            global board
            global adjacent
            if check_board(board):
                x = int(pp.width/2)
                y = int(pp.height/2)
            else:
                play_turn = [1,2]
                UCT = MCTS_UCT(board, play_turn, time=5, max_actions=7)
                move = UCT.get_action()
                x,y = move
            i += 1
            if pp.terminateAI:
                return
            if isFree(x,y):
                break
        if i > 1:
            pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
        pp.do_mymove(x, y)
    except:
        # logTraceBack()
        raise Exception("1")

def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x][y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)


pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	main()
