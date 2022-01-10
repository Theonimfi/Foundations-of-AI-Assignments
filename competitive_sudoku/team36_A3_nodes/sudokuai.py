#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import numpy as np
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


MAX_DEPTH = 50
END_GAME = 21
C = 0.4

class MCST_Node():
    def __init__(self, all_moves, gameCopy, parent=None, depth=0):
        super().__init__()

        self.parent = parent
        self.children = []
        self.n = 0
        self.v = 0
        self.depth = depth

        self.all_moves = all_moves

        self.unmade_moves = all_moves

        self.gameCopy = gameCopy

        self.results = [0, 0]


    # If start mod 2 is zero then the current agent is not our a3 agent
        if depth % 2 == 0:
            self.isa3agent = False
        else:
            self.isa3agent = True

    def expand(self):
        move = self.unmade_moves.pop()
        nextMoves = update_moves(self.all_moves, move.i, move.j, move.value)
        self.gameCopy.board.put(move.i, move.j, move.value)

        child = MCST_Node(nextMoves, self.gameCopy, self, self.depth+1)
        self.children.append(child)

        return child
    
    def roll_out(self):
        nextMoves = self.all_moves
        move_score = 0
        while nextMoves:
            print('yas')
            next_random_move = random.choice(nextMoves)

            if self.isa3agent:
                move_score = move_score - score_move(next_random_move, self.gameCopy)
                self.isa3agent = False
            else:
                move_score = move_score + score_move(next_random_move, self.gameCopy)
                self.isa3agent = True
            
            self.gameCopy.board.put(next_random_move.i, next_random_move.j, next_random_move.value)
            nextMoves = update_moves(nextMoves, next_random_move.i, next_random_move.j, next_random_move.value)
            
        return move_score

    def backpropagate(self, result):
        self.n += 1
        self.v += result
        self.results[result] += 1

        if self.parent:
            self.parent.backpropagate(result)

    def UCT(self):

        moves_UCB = [(c.v / c.n) + C * np.sqrt((2 * np.log(self.n) / c.n)) if c.n > 0 else float("inf") for c in self.children]
        print(moves_UCB, np.argmax(moves_UCB))
        return self.children[np.argmax(moves_UCB)]

    def select_best_child(self):

        current_node = self

        while current_node.children != []:

            if current_node.unmade_moves != []:
                return current_node.expand()
            else:
                print(current_node)
                current_node = current_node.UCT()
        
        return current_node

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

        self.last_moves = []

        self.taboo_moves = []

    def compute_best_move(self, game_state: GameState) -> None:

        N = game_state.board.N

        # Find all legal and non taboo moves
        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) 
                     for value in self.get_values(i, j, game_state) if self.possible(i, j, value, game_state)]

        # Propose a random move first in case there is no time to implement minimax.
        move = random.choice(all_moves)
        self.propose_move(move)

        # Call monte_carlo function with 900 number of iterations, to find the best move.
        # self.monte_carlo(game_state, game_state, all_moves, float("-inf"), True, [], all_moves[0], 900, 1, 0)

        self.mon_car(game_state, game_state, all_moves, float("-inf"), True, [], all_moves[0], 900, 1, 0)
    
    def mon_car(
        self,
        game_state: GameState,
        initial_game_state: GameState,
        all_moves,
        max_score,
        firstRound,
        evaluations,
        initial_move,
        iterations,
        start,
        move_score
    ):
        gameCopy = game_state
        root = MCST_Node( all_moves, gameCopy, 0)

        while root.unmade_moves:
            root.expand()
       
        for i in range(100):
            nextMove = root.select_best_child()
            result = nextMove.roll_out()
            nextMove.backpropagate(result)


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



    def monte_carlo(
        self,
        game_state: GameState,
        initial_game_state: GameState,
        all_moves,
        max_score,
        firstRound,
        evaluations,
        initial_move,
        iterations,
        start,
        move_score
    ):
        """
        The monte_carlo function searches for the best move by simulating the game. For every possible move, it completes
        the game randomly and it calculates the score. Then it keeps the move with the best score. If this move turns out to
        be worst move than others in another game simulation, then it goes back and it gets another better move.

        @param game_state: Current Game state.
        @param initial_game_state: Initial Game state.
        @param all_moves: List of all moves that needs investigation.
        @param max_score: The max score.
        @param firstRound: True if it's agent's first turn False if its the game simulation.
        @param evaluations: Includes tuples with each moves and their scores.
        @param initial_move: The move that the agent chose.
        @param iterations: The number of game simulations.
        @param start: Indicates which turn is it.
        @param move_score: Keeps track of the score.
        """

        # If there are no more iterations or moves return
        if iterations == 0 or len(all_moves) == 0:
            return

        # Reduce number of iterations
        iterations = iterations - 1
        print(iterations)

        # If no max score is found then found_max_score remains False
        found_max_score = False

        # The round's max score
        round_max_score = float("-inf")

        # If start mod 2 is zero then the current agent is not our a3 agent
        if start % 2 == 0:
            isa3agent = False
        else:
            isa3agent = True

        # Increase start value
        start = start + 1

        # For every possible move, complete the game randomly and calculate the score of every game. If the
        # game is the first round then save all scores and moves in the evaluations list and save also the best move
        # with thw highest score. If the game is not the first round then save the highest score of this round
        for move in all_moves:
            move_score = 0
            gameCopy = game_state
            if isa3agent:
                move_score = move_score + score_move(move,gameCopy)
                isotheragent = True
            else:
                move_score = move_score - score_move(move, gameCopy)
                isotheragent = False
            gameCopy.board.put(move.i, move.j, move.value)
            nextMoves = update_moves(all_moves, move.i, move.j, move.value)
            
            while nextMoves:
                next_random_move = random.choice(nextMoves)
                if isotheragent:
                    move_score = move_score - score_move(next_random_move, gameCopy)
                    isotheragent = False
                else:
                    move_score = move_score + score_move(next_random_move, gameCopy)
                    isotheragent = True
                gameCopy.board.put(next_random_move.i, next_random_move.j, next_random_move.value)
                nextMoves = update_moves(nextMoves, next_random_move.i, next_random_move.j, next_random_move.value)
                # print("played a random move")

            if firstRound:
                evaluations.append((move, move_score))
                if move_score > max_score:
                    max_score = move_score
                    best_move = move
                    found_max_score = True
            else:
                if move_score > round_max_score:
                    round_max_score = move_score

        # If it's the first round propose the best move and call again the monte carlo function for another
        # game simulation
        if firstRound:
            gameCopy = game_state
            initial_move = best_move
            gameCopy.board.put(best_move.i, best_move.j, best_move.value)
            updated_moves = update_moves(all_moves, best_move.i, best_move.j, best_move.value)
            self.propose_move(best_move)
            self.monte_carlo(gameCopy, game_state, updated_moves,max_score,False,evaluations, initial_move , iterations, start, max_score)
        else:
            # If it's not the first round propose then if there is a max score then call again the monte carlo function
            # otherwise, find a move with the highest score and call again monte carlo function

            if found_max_score:
                gameCopy = game_state
                gameCopy.board.put(best_move.i, best_move.j, best_move.value)
                updated_moves = update_moves(all_moves, best_move.i, best_move.j, best_move.value)
                self.propose_move(initial_move)
                self.monte_carlo(gameCopy, initial_game_state, updated_moves, max_score, False, evaluations, initial_move, iterations, start, round_max_score)
            else:
                for index, item in enumerate(evaluations):
                    itemlist = list(item)
                    if itemlist[0] == initial_move:
                        itemlist[1] = round_max_score
                        item = tuple(itemlist)
                        evaluations[index] = item
                        break;

                new_max_score = round_max_score
                new_best_move = initial_move
                for move, score in evaluations:
                    if score > new_max_score:
                        new_max_score = score
                        new_best_move = move

                gameCopy = initial_game_state
                gameCopy.board.put(new_best_move.i, new_best_move.j, new_best_move.value)
                updated_moves = update_moves(all_moves, new_best_move.i, new_best_move.j, new_best_move.value)

                # Propose the new best move that the agent founds
                self.propose_move(new_best_move)
                self.monte_carlo(gameCopy, initial_game_state, updated_moves, max_score, False, evaluations, new_best_move, iterations, 1, new_max_score)

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
