# -*- coding: utf-8 -*-
"""
alpha-beta pruning method
created by Liguo Chen
"""

from util import *
import copy


class Node:
    def __init__(self, player=1, successor=[], isLeaf=False, value=None, action=None):
        if player == 1:
            self.rule = 'max'
        elif player == 2:
            self.rule = 'min'
        self.successor = successor
        self.isLeaf = isLeaf
        self.value = value
        self.action = action
        # action 存上一步落子的坐标，其实就是前驱节点的坐标信息
        # # which action to get this state, its board value is 3 - player


def value(node, alpha, beta):

    if node.rule == 'max':
        return maxValue(node, alpha, beta)
    else:
        return minValue(node, alpha, beta)


def maxValue(node, alpha, beta):

    if node.isLeaf:
        return node.value, None  # means no actions next
    else:
        action = None
        temp_alpha = alpha
        up_bound = float('-inf')
        # print 'len', len(node.successor)
        for child in node.successor:
            # print child.value, temp_alpha, beta
            if minValue(child, temp_alpha, beta)[0] > up_bound:
                # print 'hhh', minValue(child, temp_alpha, beta)[0], up_bound
                # print 'first if called'
                up_bound = minValue(child, temp_alpha, beta)[0]
                action = child.action  # renew action
            if up_bound >= beta:
                # print 'second if called'
                return up_bound, None  # pruning, don't care how to arrive it
            temp_alpha = max(temp_alpha, up_bound)
        return up_bound, action


def minValue(node, alpha, beta):

    if node.isLeaf:
        return node.value, None
    else:
        action = None
        temp_beta = beta
        low_bound = float('inf')
        for child in node.successor:
            if maxValue(child, alpha, temp_beta)[0] < low_bound:
                action = child.action  # renew action
                low_bound = maxValue(child, alpha, temp_beta)[0]
            if low_bound <= alpha:
                return low_bound, None  # pruning, don't care how to arrive it
            temp_beta = min(low_bound, temp_beta)
        return low_bound, action

def critical(board):

    special_pattern_player_1 = is_special_pattern(board = board, player = 1)
    key_1 = list(special_pattern_player_1.keys())
    special_pattern_player_2 = is_special_pattern(board = board, player = 2)
    key_2 = list(special_pattern_player_2.keys())
    # special_pattern_merge = Merge(special_pattern_player_1, special_pattern_player_2)
    # special_pattern = list(special_pattern_merge.keys())

    # 所有特殊情形的列表
    for sp in key_1:
        if sp in ['H4','C4']:
            return '4_2'
    for sp in key_2:
        if sp in ['H4','C4']:
            return '4_1'
    return None

def constructTree(n, board, player, action, possible_position=None):
    """
    construct a tree using given information, and return the root node
    :param
        n: the depth of the tree
        board: the whole board
        player: whose turn
        prob_pos: prob_pos for the temporary board
        action: how to get the root node of this tree
    :return: root node
    """
    max_branch_num = 7
    # 限制分支因子，不考虑过多局面
    node = Node(player=player, action=action)
    successors = []
    if possible_position == None:
        # 没有给定可选位置，我们自己现场计算
        logDebug("Point 1.")
        possible_position = possible_pos(board)
        logDebug("Point 2.")
        if possible_position == None:
            # 真的没有可选位置，😅
            return None

    is_critical = critical(board)
    new_board = copy.deepcopy(board)
    if is_critical == '4_1':
    # 我方四子连珠
        for pos in possible_position:
            new_board[pos[0]][pos[1]] = player
            new_special_pattern = is_special_pattern(board = new_board, player = player)
            old_special_pattern = is_special_pattern(board = board, player = player)
            if new_special_pattern["H4"] != old_special_pattern["H4"] or new_special_pattern["C4"] != old_special_pattern["C4"]:
                node = Node(player=player, action=action)
                successors = []
                successors.append(Node(player = 3-player, isLeaf = True, value = 1000000000, action = pos))
                # action 是到达这个节点，我们落子的位置
                node.successor = successors
                return node
            
    top_position = []

    if n == 1:
    # 树的深度只有一层
        if len(possible_position) < max_branch_num:
            for pos in possible_position:
                # :pos: 坐标 (x, y)
                # :prob_position: 可选位置，坐标的列表
                copy_board = copy.deepcopy(board)
                # 棋盘当前状态的拷贝（或许可以直接用深拷贝拷贝列表，不用一个一个位置去循环）
                copy_board[pos[0]][pos[1]] = player
                # 在当前位置放置当前棋手的棋子
                # player == 1 or 2
                temp_value = board_score(copy_board)
                # :util::board_evaluation:返回当前整个棋局的评分
                # 大评分对我们好，小评分对对方好
                # print temp_value
                # successors.append(Node(player=3-player, isLeaf=True, value=board_evaluation(board_copy), action=pos))
                successors.append(Node(player=3 - player, isLeaf=True, value=temp_value, action=pos))
                # 一层搜索树，下一个节点就是叶节点
                # player = 3 - player 完成棋手轮换
                # TODO: need to delete
        else:
        # 如果分支因子过大，只考虑落子后局面最好的前k个
            for pos in possible_position:
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = player
                temp_value = board_score(board_copy)
                # :util::board_evaluation: 返回当前整个棋局的评分
                top_position.append(temp_value)
            temp = copy.deepcopy(top_position[:])
            # deepcopy
            temp.sort(reverse=True)
            # 从大到小排列
            for v in temp[0:max_branch_num]:
                pos = possible_position[top_position.index(v)]
                successors.append(Node(player=3 - player, isLeaf=True, value=v, action=pos))
                # 一层，后继节点是叶节点

    else:
    # 多层搜索树🌲
        if len(possible_position) < max_branch_num:
            # i = 0
            for pos in possible_position:
                # i += 1
                # print pos, 'else called', i
                copy_board = copy.deepcopy(board)
                copy_board[pos[0]][pos[1]] = player
                # print board_copy
                successors.append(constructTree(n-1, copy_board, 3-player, pos, update_possible_pos(pos, possible_position)))
                # 递归的调用
        else:
            for pos in possible_position:
                board_copy = copy.deepcopy(board)
                board_copy[pos[0]][pos[1]] = player
                top_position.append(board_score(board_copy))
            temp = copy.deepcopy(top_position[:])
            temp.sort(reverse=True)
            for v in temp[0:max_branch_num]:
                pos = possible_position[top_position.index(v)]
                copy_board = copy.deepcopy(board)
                copy_board[pos[0]][pos[1]] = player
                successors.append(constructTree(n - 1, copy_board, 3 - player, pos, update_possible_pos(pos, possible_position)))
    node.successor = successors
    return node


def pruning_brain():
    logDebug("Some message 1")
    try:
        max_DEPTH = 1
        root_node = constructTree(max_DEPTH, board, 1, None)
        logDebug("Execution.")
        if root_node is None:
            logDebug("First Move!")
            pp.do_mymove(10, 10)
        else:
            max_value, action = value(root_node, float("-inf"), float("inf"))
            pp.do_mymove(action[0], action[1])

    except:
        logTraceBack()
