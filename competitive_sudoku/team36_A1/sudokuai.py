#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

# # python .\simulate_game.py --first greedy_player --second team36_A1 --board .\boards\random-3x3.txt


import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

        self.MAX_DEPTH = 50
    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def possible(i, j, value):
            not_taboo = game_state.board.get(i, j) == SudokuBoard.empty \
                        and not TabooMove(i, j, value) in game_state.taboo_moves

            if not not_taboo:
                return False

            values = get_surrounding_values(i, j, game_state)
            
            return value not in values
        

        # def do_minimax(game_state, all_moves):
        #     state_stack = []

        #     for i in range(self.MAX_DEPTH):

        def score_move(Move):
            score = 0
            complete_row = len(get_row(Move.i, game_state)) == game_state.board.N-1
            complete_column = len(get_column(Move.j, game_state)) == game_state.board.N-1
            complete_box = len(get_block(Move.i, Move.j, game_state)) == game_state.board.N-1


            if complete_row and complete_column and complete_box:
                score += 7
            elif complete_row and complete_column:
                score += 3
            elif (complete_row and complete_box) or (complete_column and complete_box):
                score += 3
            elif complete_row or complete_column or complete_box:
                score += 1
            return score

        def minimax(game_state, depth, alpha, beta, isMaximisingPlayer, max_depth=2):

            N = game_state.board.N
            current_scores = game_state.scores
            all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]
            
            if depth==max_depth or len(all_moves) == 0:
                return None, current_scores[1] - current_scores[0]
    
            if isMaximisingPlayer:
                max_eval = float('-inf')
                for move in all_moves:
                    move_score = score_move(move)

                    game_state.scores[1] += move_score
                    game_state.board.put(move.i, move.j, move.value)

                    # print(f"{depth}/{max_depth}, Maximazing move: {move}, {move_score}, {game_state.scores[1]- game_state.scores[0]}")
                    
                    current_eval = minimax(game_state, depth+1, alpha, beta, False, max_depth)[1]

                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    game_state.scores[1] -= move_score

                    if float(current_eval) > max_eval:
                        max_eval = current_eval
                        best_move = move

                    alpha = max(alpha, current_eval)
                    if beta <= alpha:
                        break;       

                # print(depth, max_eval)             
                return best_move, max_eval
            else:
                min_eval = float('inf')
                for move in all_moves:
    
                    move_score = score_move(move)
                    game_state.scores[0] += move_score
                
                    game_state.board.put(move.i, move.j, move.value)

                    current_eval = minimax(game_state, depth+1, alpha, beta, True, max_depth)[1]

                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    game_state.scores[0] -= move_score

                    if float(current_eval) < min_eval:
                        min_eval = current_eval
                        best_move = move
                    beta = min(alpha, current_eval)
                    if beta <= alpha:
                        break;  
                # print(depth, min_eval)             

                return best_move, min_eval



        def do_minimax_rec(game_state):
            best_move = None
            
            for i in range(1, self.MAX_DEPTH):
                best_move = minimax(game_state,0,float('-inf'),float('inf'),True, max_depth=i)[0]

                self.propose_move(best_move)

                print(f"Depth: {i}, Best move: {best_move}, score: {score_move(best_move)}")


        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]\
            
        move = random.choice(all_moves)
        self.propose_move(move)

        do_minimax_rec(game_state)


def get_surrounding_values(i,j, game_state: GameState):
    N = game_state.board.N
    values = []

    # get values in row
    values.extend(get_row(i, game_state))
    
    # get values in column
    values.extend(get_column(j, game_state))
    
    # get values in block
    values.extend(get_block(i,j, game_state))

    return values

def get_column(j, game_state):
    return [game_state.board.get(z, j) for z in range(game_state.board.N) if game_state.board.get(z, j) != SudokuBoard.empty]

def get_row(i, game_state):
    return [game_state.board.get(i, z) for z in range(game_state.board.N) if game_state.board.get(i, z) != SudokuBoard.empty]


def get_block(i,j, game_state):
    i_start = int(i/game_state.board.n)*game_state.board.n
    j_start = int(j/game_state.board.m)*game_state.board.m
    return [game_state.board.get(x, y) for x in range(i_start, i_start+game_state.board.n) for y in range(j_start, j_start+game_state.board.m) if game_state.board.get(x,y) != SudokuBoard.empty]
