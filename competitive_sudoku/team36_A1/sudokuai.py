#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import datetime


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

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
        
        def minimax (game_state, depth, alpha, beta, isMaximisingPlayer):
            if depth == 3:
                current_scores = game_state.scores
                return  None, current_scores[0] - current_scores[1]
            
            N = game_state.board.N
            all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]
            
            if isMaximisingPlayer:
                max_eval = float('-inf')
                for move in all_moves:
                    game_state.moves.append(move)
                    current_eval = minimax(game_state, depth+1, alpha, beta, False)[1]
                    game_state.moves.pop()
                    if float(current_eval) > max_eval:
                        max_eval = current_eval
                        best_move = move
                    alpha = max(alpha, current_eval)
                    if beta <= alpha:
                        break;                    
                return best_move, max_eval
            else:
                min_eval = float('inf')
                for move in all_moves:
                    game_state.moves.append(move)
                    current_eval = minimax(game_state, depth+1, alpha, beta, True)[1]
                    game_state.moves.pop()
                    if float(current_eval) < min_eval:
                        min_eval = current_eval
                        best_move = move
                    alpha = min(alpha, current_eval)
                    if beta <= alpha:
                        break;  
                return best_move, min_eval

        move = minimax(game_state,0,float('-inf'),float('inf'),True)[0]

        self.propose_move(move)
            

        def score_move(moves):
            scores = []
            for move in moves:
                score = 0
                complete_row = "check move against gamestate"
                complete_column = "check move against gamestate"
                complete_box = "check move against gamestate"
                if complete_row and complete_column and complete_box:
                    score += 7
                elif complete_row and complete_column:
                    score += 3
                elif complete_row or complete_column:
                    score += 1
                else:
                    continue
            return scores
        # instead of returning the score you need to return the move that has the maximum score
        # move = move[max(score_move(all_moves))]

        """for move in all_moves:
            print(move.i, move.j, move.value)"""

        # move = random.choice(all_moves)
        # print(move.i, move.j, move.value, possible(move.i, move.j, move.value))
        # self.propose_move(move)
        while True:
            time.sleep(0.2)
            # self.propose_move(random.choice(all_moves))


def get_surrounding_values(i,j, game_state: GameState):
    N = game_state.board.N
    values = []

    # get values in row
    values.extend([game_state.board.get(i, z) for z in range(N) if game_state.board.get(i, z) != SudokuBoard.empty])
    
    # get values in column
    values.extend([game_state.board.get(z, j) for z in range(N) if game_state.board.get(z, j) != SudokuBoard.empty])
    
    # get values in block
    i_start = int(i/game_state.board.n)*game_state.board.n
    j_start = int(j/game_state.board.n)*game_state.board.n
    values.extend([game_state.board.get(x, y) for x in range(i_start, i_start+game_state.board.n) for y in range(j_start, j_start+game_state.board.n) if game_state.board.get(x,y) != SudokuBoard.empty])

    return values