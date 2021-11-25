#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

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

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def possible(i, j, value):
            not_taboo = game_state.board.get(i, j) == SudokuBoard.empty \
                        and not TabooMove(i, j, value) in game_state.taboo_moves
            # print(i, j, value, not_taboo)
            values = []
            for z in range(N):
                values.append(game_state.board.get(i, z))
                # print(game_state.board.get(move.i, z))
            for z in range(N):
                values.append(game_state.board.get(z, j))
            valid_move = (game_state.board.get(i, j) == SudokuBoard.empty and value not in values)

            return (not_taboo and valid_move), values

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1)
                     if possible(i, j, value)[0]]

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

        move = random.choice(all_moves)
        print(move.i, move.j, move.value, possible(move.i, move.j, move.value))
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))

