#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import sys
import numpy as np
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy

C = 3
N_simulations = 1000000

class MCST_Node():
    """
        The monte_carlo function searches for the best move by simulating the game. For every game state, it selects
        a move, its expands it, it simulates the game by choosing random moves to complete it and then it calculates
        the UCT. Finally, it backpropagates the game by updated the UCT value in every visited node.

        @param gameCopy: Deepcopy of the game state.
        @param n_empty: Number of empty cells.
        @param all_moves: List of all moves that needs investigation.
        @param eval: The total score of a game.
        @param parent: The parent node.
        @param move: A move of type Move.
        @param move_score: The score of a move.
        @param depth: The depth. Indcated the current agent.
    """

    def __init__(self, all_moves, gameCopy, n_empty, eval=0, parent=None, move=None, move_score=0, depth=0):
        super().__init__()
        self.move=move
        self.move_score = move_score
        self.eval = eval
        
        self.parent = parent
        self.children = []

        self.depth = depth


        self.all_moves = all_moves
        self.unmade_moves = copy.copy(all_moves)

        self.gameCopy = gameCopy

        self.results = [0, 0, 0]
        self.n = 0
        self.v = 0

        self.n_empty = n_empty

    # If start mod 2 is zero then the current agent is not our a3 agent
        if depth % 2 != 0:
            self.isa3agent = False
        else:
            self.isa3agent = True

    def expand(self):
        """
        The agent expands the initial node by finding the children of the node.
        """
        # Select move to expand
        move = self.unmade_moves.pop()
        
        move_score = score_move(move, self.gameCopy)

        # add or substract score based on which player makes move
        if self.isa3agent:
            eval = self.eval+move_score
        else:
            eval = self.eval-move_score

        nextMoves = update_moves(self.all_moves, move.i, move.j, move.value)
    
        gameCopy = copy.deepcopy(self.gameCopy)
        gameCopy.board.put(move.i, move.j, move.value)
    
        # Create new node with updated gamestate and score
        child = MCST_Node(nextMoves, gameCopy, self.n_empty-1, parent=self, eval=eval, move=move, move_score=move_score, depth=self.depth+1)

        self.children.append(child)

        return child
    
    def roll_out(self):
        """
        The agent simulates the game. A random move from the expansion is chosen and the game from this
        move is randomly completed.
        """

        nextMoves = self.all_moves
        move_score = self.eval
        isplayer = not self.isa3agent
        
        board_copy = copy.deepcopy(self.gameCopy)

        # Play random moves till there are no more moves to make
        while nextMoves:
            next_random_move = random.choice(nextMoves)
            
            # Add or subtract based on who is playing
            if isplayer:
                move_score = move_score - score_move(next_random_move, board_copy)
            else:
                move_score = move_score + score_move(next_random_move, board_copy)

            isplayer = not isplayer

            board_copy.board.put(next_random_move.i, next_random_move.j, next_random_move.value)
            nextMoves = update_moves(nextMoves, next_random_move.i, next_random_move.j, next_random_move.value)

        empty_squares = set([(i, j) for i in range(self.gameCopy.board.N) for j in range(self.gameCopy.board.N) if board_copy.board.get(i,j) == SudokuBoard.empty])

        # Return score if game is finished else 0 because of an unsolvable position
        if len(empty_squares) == 0:
            return move_score
        else:
            return 0

    def backpropagate(self, result):
        """
        The agent backtracks the nodes that it chose to reach the expanded node and updates the UCT values.

        @param result: the results of the rollout.
        """
        self.n += 1
        self.v += result

        if result>0:
            self.results[1] += 1
        else:
            self.results[0] += 1

        if self.parent:
            self.parent.backpropagate(result)

    def UCT(self, C=2):
        """
        Calculates the UCT formula and returns the child with highest values. 
        With C=0, it selects the best performing child (to propose) 

        @param C: Value that determines how much the number of runs punishment weights


        """

        moves_UCB = [(c.v / c.n) + C * np.sqrt((2 * np.log(self.n) / c.n)) if c.n > 0 else float("inf") for c in self.children]

        return self.children[np.argmax(moves_UCB)]

    def select_best_child(self):
        """
        Finds the best child of a parent node.

        """

        current_node = self

        # Walk through search tree based on UCT, until either
        # a leaf is found to expand or till the end is reached
        while current_node.n_empty != 0:

            if current_node.unmade_moves != []:
                return current_node.expand()
            else:
                current_node = current_node.UCT(C)

        return None


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:

        N = game_state.board.N

        # Find all legal and non taboo moves
        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) 
                     for value in self.get_values(i, j, game_state) if self.possible(i, j, value, game_state)]

        # Propose a random move first in case there is no time to implement minimax.
        move = random.choice(all_moves)
        self.propose_move(move)

        # Call monte_carlo function with 900 number of iterations, to find the best move.
        self.mon_car(game_state, all_moves)


    def mon_car(
        self,
        game_state: GameState,
        all_moves,
    ):
        """
            This is the monte carlo function that repeats the monte carlo steps 109000 times if there is time left.

            @param gameCopy: The state of the game.
            @param all_moves: List of all moves that needs investigation.
        """

        gameCopy = game_state

        N = game_state.board.N
        empty_squares = set([(i, j) for i in range(N) for j in range(N) if gameCopy.board.get(i, j) == SudokuBoard.empty])

        root = MCST_Node( all_moves, gameCopy, len(empty_squares), depth=0)

        for i in range(N_simulations):

            # Selection step
            nextMove = root.select_best_child()

            if nextMove == None:
                break
            
            # Simulation (roll out) step
            result = nextMove.roll_out()

            # Backpropogate step
            nextMove.backpropagate(result)

            # Getting best move to propose
            best_move = root.UCT(C=0).move
            self.propose_move(best_move)
  

    def possible(self, i, j, value, game_state):
        """
        Checks if a move is possible to make by looking
        if it is neither a taboo move nor an already filled square.

        @param i: Row coordinate of the square
        @param j: Column coordinate of the square
        @param value: Value to be filled in
        """

        not_taboo = (
            game_state.board.get(i, j) == SudokuBoard.empty
            and not TabooMove(i, j, value) in game_state.taboo_moves
        )

        return not_taboo

    def get_values(self, i, j, game_state):
        """
        Determines for a square what kind of values can still be filled in.

        @param i: Row coordinate of the square
        @param j: Column coordinate of the square
        """

        N = game_state.board.N

        values = get_surrounding_values(i, j, game_state)

        return [value for value in range(1, N + 1) if value not in values]

######                                    ######
#       INFORMATION ON THE MOVES               #
######                                    ######


def update_moves(all_moves: list, current_i: int, current_j: int, current_value):
    """
    Updates the list of moves by creating a new list that doesn't include the illegal moves that are
    generated after applying a move.

    @param all_moves: List of all moves
    @param current_i: Row coordinate of the move
    @param current_j: Column coordinate of the move
    @param current_value: Value of the current move
    """

    new_moves = []

    for other_move in all_moves:
        if (other_move.i, other_move.j) != (current_i, current_j):

            if other_move.i != current_i and other_move.j != current_j:
                new_moves.append(other_move)

            elif (other_move.i == current_i and other_move.j != current_j) or (
                other_move.i != current_i and other_move.j == current_j
            ):

                if other_move.value != current_value:
                    new_moves.append(other_move)

    return new_moves


def score_move(move: Move, game_state: GameState) -> int:
    """The move scoring function calculates if a player will get contributed points
    for a given move. If either a block, column or row is completed 1 point is awarded
    if two of these are completed 3 points are awarded if all are completed 7 points.

        Parameters:
            move: The move to be checked.
            game_state: The current game state (board)

        Returns:
            score (int): the score of the move to be played
    """
    score = 0
    complete_row, complete_column, complete_box = completions(move.i, move.j , game_state)

    if complete_row and complete_column and complete_box:
        score += 7
    elif complete_row and complete_column:
        score += 3
    elif (complete_row and complete_box) or (complete_column and complete_box):
        score += 3
    elif complete_row or complete_column or complete_box:
        score += 1
    return score

######                                    ######
#       INFORMATION ON THE BOARD STATUS        #
######                                    ######

def completions(i, j, game_state: GameState):
    """
    Returns true if a move completes a row a column and a block.

    @param i: Row coordinate of the move
    @param j: Column coordinate of the move
    @param game_state: Current state of the game
    """

    complete_row = len(get_row(i, game_state)) == game_state.board.N - 1
    complete_column = len(get_column(j, game_state)) == game_state.board.N - 1
    complete_box = len(get_block(i, j, game_state)) == game_state.board.N - 1

    return complete_row, complete_column, complete_box

def get_surrounding_values(i: int, j: int, game_state: GameState):
    """
    Retrieve which values are in the block, row and column of
    a given square.

    Parameters:
            i: Row coordinate of the square
            j: Column coordinate of the square
            game_state: The current game state (board)

        Returns:
            values: the values in the block, row, column surrounding a square
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


def get_column(j: int, game_state: GameState):
    """Retrieve the values in a certain column with coordinate j

    Parameters:
        j: Column coordinate of the square
        game_state: The current game state (board)

    Returns:
        values: The values in the column
    """
    values = [
        game_state.board.get(z, j)
        for z in range(game_state.board.N)
        if game_state.board.get(z, j) != SudokuBoard.empty
    ]
    return values
 

def get_row(i: int, game_state: GameState):
    """Retrieve the values in a certain row with coordinate i

    Parameters:
        i: Column coordinate of the square
        game_state: The current game state (board)

    Returns:
        values: The values in the column
    """
    values = [
        game_state.board.get(i, z)
        for z in range(game_state.board.N)
        if game_state.board.get(i, z) != SudokuBoard.empty
    ]
    return values


def get_block(i: int, j: int, game_state: GameState):
    """Get all values in a block with coordinates (i, j)

    Parameters:
        i: Row number of a square in the block
        j: Column number of a square in the block
        game_state: The current game state (board)

    Returns:
        values: The values in the block
    """

    i_start = int(i / game_state.board.m) * game_state.board.m
    j_start = int(j / game_state.board.n) * game_state.board.n
    values = [
        game_state.board.get(x, y)
        for x in range(i_start, i_start + game_state.board.m)
        for y in range(j_start, j_start + game_state.board.n)
        if game_state.board.get(x, y) != SudokuBoard.empty
    ]
    return values