
from copy import deepcopy
import random
from math import log, sqrt
import itertools
import time
import re
import pisqpipe as pp
from collections import Counter
from util import *

total_visit_time = 0
parameter = 2
time_limit = 5
# 全局变量

class Node(object):
    def __init__(self, state, player):
        self.state = state
        # 传入的棋盘必须是已经deepcopy的
        self.parent = []
        self.child = []
        self.visit_count = 0
        self.win_count = 0
        self.ucb = self.get_ucb()
        self.is_leaf = True
        self.possible_actions = self.get_possible_actions()
        self.player = player
        self.from_what_action = (10,10)
        # 用来记录通过哪一个行动到达当前节点

    def get_ucb(self):
        # logDebug("get_ucb(self)")
        global total_visit_time
        global parameter
        N = total_visit_time
        n = self.visit_count
        C = parameter
        if self.visit_count != 0:
            win_rate = self.win_count / self.visit_count
            ucb_value = win_rate + C * sqrt(log(N) / n)
        else:
            ucb_value = 1000000
        # UCB公式
        return ucb_value

    def get_possible_actions(self):
        # logDebug("get_possible_actions(self):")
        # 针对某个节点，计算所有可能落子的位置，返回tuple的list
        C = 1
        possible_actions = []
        # 附近的定义，可以调整
        # 只把当前落子位置的附近放进去
        for x in range(20):
            for y in range(20):
                if self.state[x][y] == 0:
                # 考察空白比考察落子位置效率更高，虽然看起来反直觉
                    for i in range(-C, C+1):
                        for j in range(-C, C+1):
                            # i,j分别是水平和垂直摆动项
                            if i != 0 or j != 0:
                                # 排除自身
                                if self.state[x+i][y+j] != 0:
                                    pos = (x, y)
                                    if pos not in possible_actions:
                                        # 防止重复加入
                                        # logDebug(str((x,y))+str((i, j)))
                                        possible_actions.append((x,y))
                                        i = C+1
                                        j = C+1
                                        # 相当于break
        return possible_actions
    
    def update_possible_actions(self, action):
        # logDebug("update_possible_actions(self, action):")

        # 基于当前possible_actions和新的行动，动态更新possible_actions

        x = action[0]
        y = action[1]

        new_actions = deepcopy(self.possible_actions)
        if action in new_actions:
            # 其实一定在，为了鲁棒性起见还是判断一下
            new_actions.remove(action)
        
        # 针对新落子位置action，计算周围可能落子位置
        C = 1
        # 附近的定义，可以调整
        for i in range(-C, C+1):
            for j in range(-C, C+1):
                # i,j分别是水平和垂直摆动项
                if i != 0 or j != 0:
                    # 排除自身
                    if self.state[x+i][y+j] == 0:
                        pos = (x+i, y+j)
                        if pos not in new_actions:
                            new_actions.append(pos)


def is_special_class(array, color):
    # logDebug("is_special_class(array, color)")
    # 扫描棋盘，记录当前场上的特殊棋形
    # 用于判断是否达到终止状态
    """
    judge whether the several chess given in the list form a special class
    :param
        array: the board of gomoku
        color: the index of color, 1: black, 2: white
    :return:
        Counter: ({class: num of this class}, ...)
    """

    # add judgement here. Details in 'http://zjh776.iteye.com/blog/1979748'

    def _black_color(array):
        height, width = len(array), len(array[0])
        for i in range(height):
            for j in range(width):
                array[i][j] = (3 - array[i][j]) % 3
        return array

    if color == 2:
        list_str = _black_color(array)

    class_dict = {("WIN", (), ()): "11111"
                  }

    height, width = len(array), len(array[0])
    class_counter = Counter()

    # scan by row
    for row_idx, row in enumerate(array):
        list_str = "".join(map(str, row))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    # scan by col
    for col_idx in range(width):
        col = [a[col_idx] for a in array]
        list_str = "".join(map(str, col))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    # scan by diag_1, from TL to BR
    for dist in range(-width + 1, height):
        row_ini, col_ini = (0, -dist) if dist < 0 else (dist, 0)
        diag = [array[i][j] for i in range(
            row_ini, height) for j in range(col_ini, width) if i - j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    # scan by diag_2, from BL to TR
    for dist in range(0, width + height - 1):
        row_ini, col_ini = (dist, 0) if dist < height else (
            height - 1, dist - height + 1)
        diag = [array[i][j] for i in range(
            row_ini, -1, -1) for j in range(col_ini, width) if i + j == dist]
        list_str = "".join(map(str, diag))
        for key in class_dict:
            class_counter[key[0]] += len(re.findall(class_dict[key], list_str))

    return class_counter

class MCTree(object):
    def __init__(self, root = None):
        self.root = root

    def run_one_time(self):
        # logDebug("run one time")
        # 运行一次模拟，这个函数运行以后，总会进行一次模拟，更新一次模拟结果
        global total_visit_time
        total_visit_time += 1
        current = self.root
        # logDebug(str(current.from_what_action))

        while not current.is_leaf:
            # logDebug("not current.is_leaf")
            # 如果当前节点不是叶子节点，我们找其中UCB值最大的，更新当前节点
            max_ucb = 0
            max_node = current
            for candidate in current.child:
                # logDebug("candidate in current.child")
                if candidate.ucb > max_ucb:
                    # logDebug(str(candidate.ucb))
                    max_ucb = candidate.ucb
                    max_node = candidate
            current = max_node

        # 如果当前节点是叶子节点，我们考察其是否被访问过
        if current.visit_count == 0:
            # 如果没被访问过，我们直接进行模拟
            self.roll_out(current)
            # logDebug("current.visit_count == 0")
        else:
            # 如果访问过了，我们对其进行扩展
            # logDebug("current.visit_count != 0")
            self.expand(current)
            # logDebug("len(current.child)"+str(len(current.child)))
            current = current.child[0]
            # 我们从被扩展的节点的孩子中，任选一个更新当前节点，并进行模拟
            self.roll_out(current)
           
    def expand(self, node):
        # logDebug("expand(self, node)")
        # 当前节点被访问过时，扩展当前节点，把当前节点所有可行的行动加入树中，作为当前节点的孩子
        node.child = []
        for x,y in node.possible_actions:
            # logDebug("in expand for loop")
            action = (x,y)

            new_state = deepcopy(node.state)
            new_state[x][y] = node.player
            new_player = 3 - node.player
            new_node = Node(state = new_state, player = new_player)

            new_node.parent = node
            new_node.possible_actions = new_node.get_possible_actions()
            new_node.from_what_action = action
            node.child.append(new_node)
            
            node.is_leaf = False

    def roll_out(self, node):
        # logDebug("roll_out(self, node)")
        # 对当前节点进行MC模拟，双方随机落子直至游戏结束
        if self.isTerminal(node)[0]:
            # logDebug(str(self.isTerminal(node)[0]))

            reward = self.isTerminal(node)[1]
            self.Backpropagate(node, reward)
            return

        for i in range(15):
            # logDebug(str(node.possible_actions))
            if len(node.possible_actions) == 0:
                break   # 没有可以下的地方了。
            player = node.player
            if self.isTerminal(node)[0]:

                reward = self.isTerminal(node)[1]
                self.Backpropagate(node, reward)
                return
            # 如果现在这个结点是自己在下，从空的位置中随便找一个下。
            action = node.possible_actions.pop(0)
            node.state[action[0]][action[1]] == 1
            node.possible_actions = node.get_possible_actions()
            player = 3 - player
        self.Backpropagate(node, reward = 0.3 )
        # logDebug(str(self.root.visit_count))
        return

    def Backpropagate(self, node, reward):
        # logDebug("Backpropagate(self, node, reward)")
        # 后向传播，更新当前节点以及所有上方节点的访问次数和获胜次数
        # 通过递归的方式进行
        node.visit_count += 1
        node.win_count += reward
        if node.parent:
            self.Backpropagate(node.parent, reward)
        else:
            return

    def isTerminal(self, node):
        # logDebug("isTerminal(self, node)")
        # 判断游戏是不是已经结束了，并判断获胜的一方
        num1 = is_special_class(node.state, 1)["Win"]
        num2 = is_special_class(node.state, 2)["Win"]
        if num1 > 0:
            return True, 1
        elif num2 > 0:
            return True, 0
        return False, 1

class MCTS(object):
    # 反复模拟直至时间耗尽，之后选择最优行动
    def __init__(self, state):
        self.start_time = None
        self.state = state

    def get_start_time(self):
        # logDebug("get_start_time(self)")
        self.start_time = time.time()
    
    def construct_tree(self):
        # logDebug("construct_tree(self)")
        # 在时间限制内尽可能的多进行模拟，构建MCtree
        self.get_start_time()
        # 设置开始时间
        current_node = Node(state = self.state, player = 1)
        # 根据当前棋盘状况建立节点，作为根节点
        tree = MCTree(root = current_node)
        while time.time() - self.start_time < time_limit:
            tree.run_one_time()
        return tree

def pick_best_action(MCtree):

    # logDebug("pick_best_action(MCtree)")
    # 使用树搜索算法，选择最优节点，我们选择访问次数最多或者胜率最高的节点
    # 我们只需要在一步孩子中寻找即可，因为更下层的节点会回溯更新上面的节点
    # 所以访问次数最高的节点一定是一步孩子，并且由此我们可以得到最优行动
    # 返回最优行动
    max_visit_count = 0
    max_node = MCtree.root
    # logDebug("Some message 100"+str(len(MCtree.root.child)))
    for node in MCtree.root.child:
        # logDebug("visit_count"+str(node.visit_count))
        # logDebug("from_what_action"+str(node.from_what_action))
        # logDebug("Some message 200")
        if node.visit_count >= max_visit_count:
            max_visit_count = node.visit_count
            max_node = node
            # logDebug(str(max_node.from_what_action))
    return max_node.from_what_action

def mcts_brain():
    # logDebug("Some message 1")
    try:
        # root_node = constructTree(max_DEPTH, board, 1, None)
        # logDebug("problem = MCTS(state = board)")
        board_copy = deepcopy(board)
        problem = MCTS(state = board_copy)
        
        # board 是从 util 中传入的全局变量
        # logDebug("tree = problem.construct_tree()")
        tree = problem.construct_tree()
        
        # logDebug("action = pick_best_action(tree)")
        action = pick_best_action(tree)
        
        pp.do_mymove(action[0], action[1])

        # if root_node is None:
        #     pp.do_mymove(10, 10)
        # else:
        #     # max_value, action = value(root_node, float("-inf"), float("inf"))
        #     pp.do_mymove(action[0], action[1])
    except:
        logTraceBack()




        



        
