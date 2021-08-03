import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = 'name="AI-final", author="Wenqian Zhang", version="1.0", country="China"'

MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


def brain_init():
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	pp.pipeOut("OK")

def brain_restart():
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

# def brain_turn():
# 	if pp.terminateAI:
# 		return
# 	i = 0
# 	while True:
# 		x = random.randint(0, pp.width)
# 		y = random.randint(0, pp.height)
# 		i += 1
# 		if pp.terminateAI:
# 			return
# 		if isFree(x,y):
# 			break
# 	if i > 1:
# 		pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
# 	pp.do_mymove(x, y)

def brain_end():
	pass

def brain_about():
	pp.pipeOut(pp.infotext)

# if DEBUG_EVAL:
# 	import win32gui
# 	def brain_eval(x, y):
# 		# TODO check if it works as expected
# 		wnd = win32gui.GetForegroundWindow()
# 		dc = win32gui.GetDC(wnd)
# 		rc = win32gui.GetClientRect(wnd)
# 		c = str(board[x][y])
# 		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
# 		win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################

# define a file for logging ...
DEBUG_LOGFILE = "C:/Users/reeddotaer/Desktop/新建文件夹/pbrain-clg.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function

def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()


######################################################################

# "overwrites" functions in pisqpipe module
# pp.brain_init = brain_init
# pp.brain_restart = brain_restart
# pp.brain_my = brain_my
# pp.brain_opponents = brain_opponents
# pp.brain_block = brain_block
# pp.brain_takeback = brain_takeback
# pp.brain_turn = brain_turn
# pp.brain_end = brain_end
# pp.brain_about = brain_about
# if DEBUG_EVAL:
# 	pp.brain_eval = brain_eval


########################################################################
import itertools
from collections import Counter
import re

# Self-added part
def possible_pos(board, scale = 1):
    """
    Get a list containing all possible positions given the board situation.
    :param board: a two-dimension list containing both players' information.
    0 -- vacant; 1 -- self; 2 -- rival
    :return: the possible position list
    """
    pos = []
    logDebug("Point 3.")
    for (x, y) in itertools.product(range(pp.width), range(pp.height)):
        if board[x][y] == 0:    # The curerent position is not occupied.
            continue

        for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
            pos_x, pos_y = (x + i - scale), (y + i - scale)
            if (pos_x, pos_y) not in pos:
                if isFree(pos_x, pos_y):
                    pos.append((pos_x, pos_y))

    if pos == []:
        return None

    return pos

def update_possible_pos(action, possible_pos, scale = 1):
    """
    According to the action and current possible postion list, get the updated
    position list.
    :param action: the action player chooses
    :param possible_pos: current possible position list
    :param scale: the radius around a occupied position
    :return: an updated possible position list
    """
    x, y = action[0], action[1]

    for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
        pos_x, pos_y = (x + i - scale), (y + i - scale)

        if ((pos_x, pos_y) not in possible_pos) and (isFree(pos_x, pos_y)):
            possible_pos.append((pos_x, pos_y))

    if (x, y) in possible_pos:
        possible_pos.remove((x, y))

    if possible_pos == []:
        return None

    return possible_pos

def is_special_pattern(board, player):
    """
    Determine whether the board contains a special pattern or not.
    Reference: https://www.iteye.com/blog/zjh776-1979748
    :param board: the current board
    :param player: 1 -- self; 2 -- rival
    :return: patterns and their counts the board contains
    """
    if player == 2:
        board = [[(3 - board[i][j])%3 for i in range(pp.height)] for j in range(pp.width)]
    # If the plyer is our rival now, convert the color for simplicity.

    pattern_dict = {("WIN", (), ()): "11111",
                  ("H4", (0, 5), ()): "011110",
                  ("C4", (0), (5)): "011112",
                  ("C4", (5), (0)): "211110",
                  ("C4", (4), ()): r"^11110",
                  ("C4", (0), ()): r"01111$",
                  ("C4", (0, 2, 6), ()): "0101110",
                  ("C4", (0, 4, 6), ()): "0111010",
                  ("C4", (0, 3, 6), ()): "0110110",
                  ("H3", (0, 4), ()): "01110",
                  ("H3", (0, 2, 5), ()): "010110",
                  ("H3", (0, 3, 5), ()): "011010",
                  ("M3", (0, 1), (5)): "001112",
                  ("M3", (0, 1), ()): r"00111$",
                  ("M3", (4, 5), (0)): "211100",
                  ("M3", (4, 5), ()): r"^11100",
                  ("M3", (0, 2), (5)): "010112",
                  ("M3", (0, 2), ()): r"01011$",
                  ("M3", (3, 5), (0)): "211010",
                  ("M3", (3, 5), ()): r"^11010",
                  ("M3", (0, 3), (5)): "011012",
                  ("M3", (0, 3), ()): r"01101$",
                  ("M3", (2, 5), (0)): "210110",
                  ("M3", (2, 5), ()): r"^10110",
                  ("M3", (1, 2), ()): "10011",
                  ("M3", (2, 3), ()): "11001",
                  ("M3", (1, 3), ()): "10101",
                  ("M3", (1, 4), (0, 6)): "2011102",
                  ("M3", (1, 4), (6)): r"^011102",
                  ("M3", (1, 4), (0)): r"201110$",
                  ("H2", (0, 1, 4), ()): "00110",
                  ("H2", (0, 3, 4), ()): "01100",
                  ("H2", (0, 2, 4), ()): "01010",
                  ("H2", (0, 2, 3, 5), ()): "010010",
                  ("M2", (0, 1, 2), (5)): "000112",
                  ("M2", (0, 1, 2), ()): r"00011$",
                  ("M2", (3, 4, 5), (0)): "211000",
                  ("M2", (3, 4, 5), ()): r"^11000",
                  ("M2", (0, 1, 3), (5)): "001012",
                  ("M2", (0, 1, 3), ()): r"00101$",
                  ("M2", (2, 4, 5), (0)): "210100",
                  ("M2", (2, 4, 5), ()): r"^10100",
                  ("M2", (0, 2, 3), (5)): "010012",
                  ("M2", (0, 2, 3), ()): r"01001$",
                  ("M2", (2, 3, 5), (0)): "210010",
                  ("M2", (2, 3, 5), ()): r"^10010",
                  ("M2", (1, 2, 3), ()): "10001",
                  ("M2", (1, 3, 5), (0, 6)): "2010102",
                  ("M2", (1, 3, 5), (0)): r"201010$",
                  ("M2", (1, 3, 5), (6)): r"^010102",
                  ("M2", (1, 4, 5), (0, 6)): "2011002",
                  ("M2", (1, 4, 5), (6)): r"^011002",
                  ("M2", (1, 4, 5), (0)): r"201100^",
                  ("M2", (1, 2, 5), (0, 6)): "2001102",
                  ("M2", (1, 2, 5), (0)): r"200110$",
                  ("M2", (1, 2, 5), (6)): r"^001102",
                  ("S4", (), (0, 5)): "211112",
                  ("S4", (), (0)): r"21111$",
                  ("S4", (), (5)): r"^11112",
                  ("S3", (), (0, 4)): "21112",
                  ("S3", (), (0)): r"2111$",
                  ("S3", (), (4)): r"^1112",
                  ("S2", (), (0, 3)): "2112",
                  ("S2", (), (3)): r"^112",
                  ("S2", (), (0)): r"211$",
                  }

    pattern_count = Counter()

    # Scan by row
    for _, row in enumerate(board):
        row_string = "".join(map(str, row))
        for i in pattern_dict.keys():
            pattern_count[i[0]] += len(re.findall(pattern_dict[i], row_string))

    # Scan by column
    for col_index in range(pp.width):
        col = [a[col_index] for a in board]
        col_string = "".join(map(str, col))
        for i in pattern_dict.keys():
            pattern_count[i[0]] += len(re.findall(pattern_dict[i], col_string))

    # Scan by the top left to bottom right diagnol
    for idx in range(1-pp.width, pp.height):
        row_idx, col_idx = (0, -idx) if idx < 0 else (idx, 0)
        diag = [board[i][j] for i in range(row_idx, pp.height) for j in range(col_idx, pp.width) if i - j == idx]
        diag_string = "".join(map(str, diag))
        for i in pattern_dict.keys():
            pattern_count[i[0]] += len(re.findall(pattern_dict[i], diag_string))

    # Scan by the top right to bottom left diagnol
    for idx in range(0, pp.width+pp.height-1):
        row_idx, col_idx = (idx, 0) if idx < pp.height else (pp.height - 1, idx - pp.height + 1)
        diag = [board[i][j] for i in range(row_idx, -1, -1) for j in range(col_idx, pp.width) if i + j == idx]
        diag_string = "".join(map(str, diag))
        for i in pattern_dict.keys():
            pattern_count[i[0]] += len(re.findall(pattern_dict[i], diag_string))

    return pattern_count

def pattern_score():
    """
    According to the pattern, give the score.
    Reference: https://www.iteye.com/blog/zjh776-1979748
    :return: pattern-score map
    """
    pattern_score = {"WIN": 1000000,
                 "H4": 50000,
                 "C4": 20000,
                 "H3": 200,
                 "M3": 50,
                 "H2": 5,
                 "M2": 3,
                 "S4": -5,
                 "S3": -5,
                 "S2": -5
                 }

    return pattern_score

def board_score(board):
    """
    Compute the the score of current board given the patterns.
    :param board: current board situation
    :return: the score
    """
    score, score1 = 0, 0

    for pattern, num in is_special_pattern(board, 1).items():
        temp = pattern_score()[pattern]*num
        if pattern == "C4" and num > 1:
            temp = 100000
        if pattern == "H3" and num > 1:
            temp = 10000
        if pattern == "H2" and num > 1:
            temp = 100
        if pattern == "C4" and num > 0 and is_special_pattern(board, 1)["H3"] > 0:
            temp = 100000      # the score of "C4H3" minus the score "H3", to avoid repeating scoring.
        if pattern == "M3" and num > 0 and is_special_pattern(board, 1)["H3"] > 0:
            temp = 1000        # the score of "H3M3" minus the score "H3", to avoid repeating scoring.
        if pattern == "H2" and num > 0 and is_special_pattern(board, 1)["M2"] > 0:
            temp = 10 - 3      # the score of "H2M2" minus the score "M2", to avoid repeating scoring.
        if temp > score:
            score = temp

    for pattern, num in is_special_pattern(board, 2).items():
        temp = pattern_score()[pattern]*num*1.1
        if pattern == "C4" and num > 1:
            temp = 300000
        if pattern == "H3" and num > 1:
            temp = 30000
        if pattern == "H2" and num > 1:
            temp = 300
        if pattern == "C4" and num > 0 and is_special_pattern(board, 2)["H3"] > 0:
            temp = 300000       # the score of "C4H3" minus the score "H3", to avoid repeating scoring.
        if pattern == "M3" and num > 0 and is_special_pattern(board, 2)["H3"] > 0:
            temp = 3000        # the score of "H3M3" minus the score "H3", to avoid repeating scoring.
        if pattern == "H2" and num > 0 and is_special_pattern(board, 2)["M2"] > 0:
            temp = 30          # the score of "H2M2" minus the score "M2", to avoid repeating scoring.
        if pattern in ["H4", "C4", "WIN"]:
            temp = 30*temp     # Ruining the rival's success has higher rank.
        if temp > score1:
            score1 = temp

    score = score - score1


    return score

#################################################################


#def main():
#	pp.main()
#
#if __name__ == "__main__":
#	main()
