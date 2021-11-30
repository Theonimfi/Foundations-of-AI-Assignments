#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

# # python .\simulate_game.py --first greedy_player --second team36_A1 --board .\boards\random-3x3.txt


import random
import time

import simulate_game
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import argparse
import sys


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def _init_(self):
        super()._init_()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def possible(i, j, value):
            not_taboo = game_state.board.get(i, j) == SudokuBoard.empty \
                        and not TabooMove(i, j, value) in game_state.taboo_moves

            return not_taboo

        def get_values(i,j, game_state):
            
            values = get_surrounding_values(i, j, game_state)
            
            return [value for value in range(1, N + 1) if value not in values]
    
        def score_move(Move):
            score = 0
            complete_row = len(get_row(Move.i, game_state)) == game_state.board.N - 1
            complete_column = len(get_column(Move.j, game_state)) == game_state.board.N - 1
            complete_box = len(get_block(Move.i, Move.j, game_state)) == game_state.board.N - 1

            if complete_row and complete_column and complete_box:
                score += 7
            elif complete_row and complete_column:
                score += 3
            elif (complete_row and complete_box) or (complete_column and complete_box):
                score += 3
            elif complete_row or complete_column or complete_box:
                score += 1
            return score

        def minimax(game_state, depth, alpha, beta, isMaximisingPlayer, current_score, empty_squares):

            N = game_state.board.N

            all_moves = [Move(i, j, value) for (i,j) in empty_squares for value in get_values(i,j,game_state) if
                         possible(i, j, value)]

            if depth == 0 or len(all_moves) == 0:
                return None, current_score

            if isMaximisingPlayer:
                max_eval = float('-inf')
                for move in all_moves:
                    move_score = score_move(move)
                    current_score += move_score
                    
                    empty_squares.remove((move.i, move.j))
                    game_state.board.put(move.i, move.j, move.value)

                    # print(f"{depth}, Maximazing move: {move}, {move_score}, {game_state.scores[1]- game_state.scores[0]}")

                    current_eval = minimax(game_state, depth - 1, alpha, beta, False, current_score, empty_squares)[1]

                    current_score -= move_score
                    
                    empty_squares.add((move.i, move.j))
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)

                    if float(current_eval) > max_eval:
                        max_eval = current_eval
                        best_move = move

                    alpha = max(alpha, max_eval)
                    if max_eval >= beta:
                        break;
                print(best_move, max_eval)
                return best_move, max_eval
            else:
                min_eval = float('inf')
                for move in all_moves:

                    move_score = score_move(move)
                    current_score -= move_score
                    
                    empty_squares.remove((move.i, move.j))
                    game_state.board.put(move.i, move.j, move.value)

                    current_eval = minimax(game_state, depth - 1, alpha, beta, True, current_score, empty_squares)[1]
    
                    current_score += move_score

                    empty_squares.add((move.i, move.j))
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)

                    if float(current_eval) < min_eval:
                        min_eval = current_eval
                        best_move = move

                    beta = min(beta, min_eval)
                    if min_eval <= alpha:
                        break;
                
                return best_move, min_eval

        start = time.time()

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in get_values(i,j,game_state) if possible(i, j, value)]

        move = random.choice(all_moves)
        print(time.time()-start)
        self.propose_move(move)

        for i in range(1, 50):
            empty_squares = set([(i, j) for i in range(N) for j in range(N) if game_state.board.get(i, j) == SudokuBoard.empty])
            best_move, eval = minimax(game_state, i, float('-inf'), float('inf'), True, 0, empty_squares)
            print(f"Depth: {i}, Best move: {best_move}, score: {score_move(best_move)}, {eval}")

            self.propose_move(best_move)


def get_surrounding_values(i, j, game_state: GameState):
    # possible_values = [value for value in range(1, N + 1)]
    values = set()

    # get values in row
    values.update(get_row(i, game_state))
    if len(values) == game_state.board.N:
        return values

    # get values in column
    values.update(get_column(j, game_state))
    if len(values) == game_state.board.N:
        return values

    # get values in block
    values.update(get_block(i, j, game_state))


    return values

def get_column(j, game_state):
    return [game_state.board.get(z, j) for z in range(game_state.board.N) if
            game_state.board.get(z, j) != SudokuBoard.empty]


def get_row(i, game_state):
    return [game_state.board.get(i, z) for z in range(game_state.board.N) if
            game_state.board.get(i, z) != SudokuBoard.empty]


def get_block(i, j, game_state):
    i_start = int(i / game_state.board.m) * game_state.board.m
    j_start = int(j / game_state.board.n) * game_state.board.n
    return [game_state.board.get(x, y) for x in range(i_start, i_start + game_state.board.m) for y in
            range(j_start, j_start + game_state.board.n) if game_state.board.get(x, y) != SudokuBoard.empty]