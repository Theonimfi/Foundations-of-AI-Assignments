#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

MAX_DEPTH = 50

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
            """
            Checks if a move is possible to make by looking
            if it is neither a taboo move nor an already filled square.

            @param i: Row coordinate of the square
            @param j: Column coordinate of the square
            @param j: Value to be filled in
            """
            
            not_taboo = game_state.board.get(i, j) == SudokuBoard.empty \
                        and not TabooMove(i, j, value) in game_state.taboo_moves

            return not_taboo

        def get_values(i,j):
            """
            Determines for a square what kind of values can still be filled in.

            @param i: Row coordinate of the square
            @param j: Column coordinate of the square
            """
            
            values = get_surrounding_values(i, j, game_state)
            
            return [value for value in range(1, N + 1) if value not in values]
    
        def minimax(game_state, depth, alpha, beta, isMaximisingPlayer, current_score, empty_squares):
            """
            The minimax algorithm creates a tree with nodes that includes the current evaluation score of every 
            possible move. By applying alpha-beta pruning to minimax, its efficiency is improved by ignoring 
            calculating the evaluation score of nodes that do not affect the final solution.
            
            @param game_state: Current Game state.
            @param depth: The depth of the searching tree.
            @param alpha: The value of the alpha of alpha-beta pruning.
            @param beta: The value of the beta of alpha-beta pruning.
            @param isMaximisingPlayer: Indicates if the player is the Max player (True) or not (False)
            @param current_score: The current evaluation score of the game.
            @param empty_squares: The number of empty squares.
            """
            # Find all legal and non taboo moves
            all_moves = [Move(i, j, value) for (i,j) in empty_squares for value in get_values(i,j) if
                         possible(i, j, value)]

            # Return the current score if the depth level equals to 0 or if there are no other moves
            if depth == 0 or len(all_moves) == 0:
                return None, current_score

            # Check if the player is the Max player
            if isMaximisingPlayer:

                # Add the lowest possible value in max_eval
                max_eval = float('-inf')

                for move in all_moves:

                    # Get the score of the move by calling the score_move function
                    move_score = score_move(move,game_state)

                    # Add the score of the move in the current score
                    current_score += move_score

                    # Remove this move from the empty squared table
                    empty_squares.remove((move.i, move.j))

                    # Add the move on the board
                    game_state.board.put(move.i, move.j, move.value)

                    # Call the minimax function. Decrease the depth and indicate that since this player is the Max the other
                    # player should be the Min (False). Save the result in the current_eval attribute.
                    current_eval = minimax(game_state, depth - 1, alpha, beta, False, current_score, empty_squares)[1]

                    # Subtract the move score from current score
                    current_score -= move_score

                    # Add the move score from the empty table
                    empty_squares.add((move.i, move.j))

                    # Remove the move score from the board
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)

                    # Save in max_eval and in best_move the highest evaluation score and its move respectively
                    if float(current_eval) > max_eval:
                        max_eval = current_eval
                        best_move = move

                    # Save the max evaluation score in alpha and if the max evaluation is larger than beta which is the min
                    # evaluation score there is no need to investigate the tree further
                    alpha = max(alpha, max_eval)
                    if max_eval >= beta:
                        break;

                # Return the best move and its evaluation score
                return best_move, max_eval
            else:
                # Add the highest possible value in max_eval
                min_eval = float('inf')
                for move in all_moves:

                    # Get the score of the move by calling the score_move function
                    move_score = score_move(move, game_state)

                    # Subtract the score of the move in the current score
                    current_score -= move_score

                    # Remove this move from the empty squared table
                    empty_squares.remove((move.i, move.j))

                    # Add the move on the board
                    game_state.board.put(move.i, move.j, move.value)

                    # Call the minimax function. Decrease the depth and indicate that since this player is the Min the other
                    # player should be the Max (True). Save the result in the current_eval attribute.
                    current_eval = minimax(game_state, depth - 1, alpha, beta, True, current_score, empty_squares)[1]

                    # Add the score of the move in the current score
                    current_score += move_score

                    # Add the move score to the empty table
                    empty_squares.add((move.i, move.j))

                    # Remove the move score from the board
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)

                    # Save in min_eval and in best_move the lowest evaluation score and its move respectively
                    if float(current_eval) < min_eval:
                        min_eval = current_eval
                        best_move = move

                    # Save the min evaluation score in beta and if the min evaluation is smaller than alpha which is the max
                    # evaluation score there is no need to investigate the tree further
                    beta = min(beta, min_eval)
                    if min_eval <= alpha:
                        break;

                # Return the best move and its evaluation score
                return best_move, min_eval

        #### MOVE PROPOSITIONING ###

        # Find all legal and non taboo moves
        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in get_values(i,j) if possible(i, j, value)]

        # Propose a random move first in case there is no time to implement minimax.
        move = random.choice(all_moves)
        self.propose_move(move)

        # Start with depth 1 and then increase depth. For every depth, call minimax and propose a move. The more time we have
        # the most accurate the move that the minimax returns
        for i in range(1, MAX_DEPTH):
            empty_squares = set([(i, j) for i in range(N) for j in range(N) if game_state.board.get(i, j) == SudokuBoard.empty])
            best_move, eval = minimax(game_state, i, float('-inf'), float('inf'), True, 0, empty_squares)

            self.propose_move(best_move)
            print(f"Depth: {i}, Best move: {best_move}, score: {score_move(best_move, game_state)}, {eval}")

def score_move(move: Move, game_state: GameState):
    """
    The move scoring function calculates if a player will get contributed points
    for a given move. If either a block, column or row is completed 1 point is awarded
    if a two of these are completed 3 points are awarded if all are completed 7 points.

    @param Move: The move to be checked.
    @param game_state: Current Game state.
    """
    score = 0
    complete_row = len(get_row(move.i, game_state)) == game_state.board.N - 1
    complete_column = len(get_column(move.j, game_state)) == game_state.board.N - 1
    complete_box = len(get_block(move.i, move.j, game_state)) == game_state.board.N - 1

    if complete_row and complete_column and complete_box:
        score += 7
    elif complete_row and complete_column:
        score += 3
    elif (complete_row and complete_box) or (complete_column and complete_box):
        score += 3
    elif complete_row or complete_column or complete_box:
        score += 1
    return score


def get_surrounding_values(i, j, game_state: GameState):
    """
    Retrieve which values are in the block, row and column of
    a given square.

    @param i: Row coordinate of the square
    @param j: Column coordinate of the square
    @param game_state: Current Game state.
    """
    values = set()

    # Get values in row
    values.update(get_row(i, game_state))
    if len(values) == game_state.board.N:
        return values

    # Get values in column
    values.update(get_column(j, game_state))
    if len(values) == game_state.board.N:
        return values

    # Get values in block
    values.update(get_block(i, j, game_state))


    return values

def get_column(j, game_state):
    """
    Get all values in a columnn

    @param j: Column number
    @param game_state: Current Game state.
    """
    return [game_state.board.get(z, j) for z in range(game_state.board.N) if
            game_state.board.get(z, j) != SudokuBoard.empty]


def get_row(i, game_state):
    """
    Get all values in a row

    @param i: Row number
    @param game_state: Current Game state.
    """
    return [game_state.board.get(i, z) for z in range(game_state.board.N) if
            game_state.board.get(i, z) != SudokuBoard.empty]


def get_block(i, j, game_state):
    """
    Get all values in a block

    @param i: Row number of a square in the block
    @param j: Column number of a square in the block
    @param game_state: Current Game state.
    """
    i_start = int(i / game_state.board.m) * game_state.board.m
    j_start = int(j / game_state.board.n) * game_state.board.n
    return [game_state.board.get(x, y) for x in range(i_start, i_start + game_state.board.m) for y in
            range(j_start, j_start + game_state.board.n) if game_state.board.get(x, y) != SudokuBoard.empty]