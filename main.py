"""
    Run this script to generate Sudoku puzzles. They are saved as images into the
    problems/ and solutions/ directories. They have reasonably hard difficulty.
"""
import numpy as np
from random import sample
from copy import deepcopy
import cv2


def pre_process_sudoku(_problem, update=True):
    """ This function takes in a sudoku problem with blank cells indicated by zeros,
    assuming that sudoku is solvable, this function tries to find all possible entries for a given blank cell,
     by considering other entries in the sudoku (by considering the constraints).
     If some cells have only one possible entry, them it assigns them and recomputes the new problem with lesser
     blank cells.
     """
    """ Choices contains all possible values for a given cell satisfying the given constraints. """
    _choices = {(i, j): list(range(1, 10)) for i in range(9) for j in range(9)}
    """ Positions contains list of cells that need to be solved. """
    _positions = []
    for i in range(9):
        for j in range(9):
            """ If some cell contains a value, then all cells in the horizontal and vertical axis containing that cell,
                cannot have that value. Also the cells in the square region (3x3) containing the cell cannot 
                have the value.  Remove those values which are not possible from choices. Also remove choices of those
                that are given in the problem. """
            if _problem[i, j] != 0:
                value = _problem[i, j]
                """ No choices for that cell, as already value specified """
                _choices[i, j] = []
                """ Remove the value from the corresponding row and column """
                for z in range(9):
                    if value in _choices[i, z]:
                        _choices[i, z].remove(value)
                    if value in _choices[z, j]:
                        _choices[z, j].remove(value)
                """ Remove from its corresponding square """
                si = (i // 3) * 3
                sj = (j // 3) * 3
                for _i in range(3):
                    for _j in range(3):
                        if value in _choices[si + _i, sj + _j]:
                            _choices[si + _i, sj + _j].remove(value)
            else:
                _positions.append((i, j))
    """Now we have the positions which need to be solved along with the possible choices for those positions/ cells"""
    """Sometimes few cells have a single possible choice. We can directly deduce these value without recursion."""
    if not update:
        return _problem, _choices, _positions
    any_update = False
    for i in range(9):
        for j in range(9):
            if len(_choices[i, j]) == 1:
                value = _choices[i, j][0]
                """Remove from choices, Remove the position and Update the problem with the deduced value."""
                _problem[i, j] = value
                any_update = True

    """Return Updated Problem, Possible Choices and Positions to Solve."""
    if not any_update:
        return _problem, _choices, _positions
    else:
        """Any changes were made tp the problem, re-compute the choices."""
        return pre_process_sudoku(_problem)


def print_sudoku(_problem):
    """ This function prints the sudoku, blank spaces when empty cells  """
    for i in range(9):
        if i > 0 and i % 3 == 0:
            print('---------+---------+---------')
        for j in range(9):
            if j > 0 and j % 3 == 0:
                print('|', end='', flush=True)
            if _problem[i, j] == 0:
                print('   ', end='', flush=True)
            else:
                print(' ', int(_problem[i, j]), ' ', sep='', end='', flush=True)
        print()


def solve_sudoku(_problem, _choices, _positions):
    """ This function solves the solution, assuming solution exists.
    This function returns one of the possible solutions """
    """Sort the positions based on the number of choices for that positions, 
    try guessing the positions with lesser choices first """
    _positions = sorted(_positions, key=lambda p: len(_choices[p]))
    """This method is used to solve the sudoku using recursion. Simply substitute a choice and check if solution is
    possible with that choice (solve the new smaller problem) else try out another choice and repeat the process."""
    if len(_positions) == 0:
        """If all indices have solution then return the problem as the solution."""
        return _problem
    """Check if choices exist for all cells whose value needs to be deduced."""
    for _position in _positions:
        if not _choices[_position]:
            """If some cell has no choice, then there is no solution possible """
            return None
    """ Get the current position/cell and for each possible, try to find a solution. """
    """ Try substituting the choices for the position with smallest number of choices """
    _position = _positions[0]
    """ Randomly sort the choices, for some amount of randomness """
    __choices = sample(_choices[_position], k=len(_choices[_position]))
    for _value in __choices:
        """ Make a copy of problem and the choices."""
        _problem_ = _problem.copy()
        _choices_ = deepcopy(_choices)
        """ Update the problem and the choices by making a choice for the current cell. """
        _problem_[_position] = _value
        _choices_[_position] = []
        _possible_solution = True

        if len(_positions) == 1:
            """If no more cells to look at then return the solution. """
            return _problem_

        """ Update the choices for all the cells that we are yet to deduce. """
        for _position_ in _positions[1:]:
            """ If the cell lies within influence """
            if _position_[0] == _position[0] or _position_[1] == _position[1] or \
                    (_position_[0]//3 == _position[0]//3 and _position_[1]//3 == _position[1]//3):
                """ Remove that value """
                if _value in _choices_[_position_]:
                    _choices_[_position_].remove(_value)
                    if not _choices_[_position_]:
                        """ If in some stage some cell has no possible choice,
                         then chosen value was not correct."""
                        _possible_solution = False
                        break
        if _possible_solution:
            _positions_ = deepcopy(_positions)
            _temp_solution = solve_sudoku(_problem_, _choices_, _positions_[1:])
            """Check if that choice yielded an solution."""
            if _temp_solution is not None:
                return _temp_solution
    """If no choice yields a solution, then no solution possible."""
    return None


def num_solution(_problem, _choices, _positions):
    """ This function solves the solution, assuming solution exists.
    This function returns 0 if no solution, 1 if single solution else a number greater than 1 """
    """Sort the positions based on the number of choices for that positions, 
    try guessing the positions with lesser choices first """
    _positions = sorted(_positions, key=lambda p: len(_choices[p]))
    """This method is used to solve the sudoku using recursion. Simply substitute a choice and check if solution is
    possible with that choice (solve the new smaller problem) else try out another choice and repeat the process."""
    if len(_positions) == 0:
        """If all indices have solution then return the problem as the solution."""
        return 1
    """Check if choices exist for all cells whose value needs to be deduced."""
    for _position in _positions:
        if not _choices[_position]:
            """If some cell has no choice, then there is no solution possible """
            return 0
    """ Get the current position/cell and for each possible, try to find a solution. """
    """ Try substituting the choices for the position with smallest number of choices """
    _position = _positions[0]
    """ Randomly sort the choices, for some amount of randomness """
    count = 0
    __choices = sample(_choices[_position], k=len(_choices[_position]))
    for _value in __choices:
        """ Make a copy of problem and the choices."""
        _problem_ = _problem.copy()
        _choices_ = deepcopy(_choices)
        """ Update the problem and the choices by making a choice for the current cell. """
        _problem_[_position] = _value
        _choices_[_position] = []
        _possible_solution = True

        if len(_positions) == 1:
            """If no more cells to look at then return the solution. """
            count += 1
            if count > 1:
                return count
            continue

        """ Update the choices for all the cells that we are yet to deduce. """
        for _position_ in _positions[1:]:
            """ If the cell lies within influence """
            if _position_[0] == _position[0] or _position_[1] == _position[1] or \
                    (_position_[0]//3 == _position[0]//3 and _position_[1]//3 == _position[1]//3):
                """ Remove that value """
                if _value in _choices_[_position_]:
                    _choices_[_position_].remove(_value)
                    if not _choices_[_position_]:
                        """ If in some stage some cell has no possible choice,
                         then chosen value was not correct."""
                        _possible_solution = False
                        break

        if _possible_solution:
            _positions_ = deepcopy(_positions)
            count += num_solution(_problem_, _choices_, _positions_[1:])
            if count > 1:
                return count
            """Check if that choice yielded an solution."""

    """If no choice yields a solution, then no solution possible."""
    return count


def validate_sudoku(_sudoku):
    """ Check the correctness of the given sudoku  """
    for i in range(9):
        for j in range(9):
            if _sudoku[i, j] == 0:
                """ If the current cell is not yet solved, ok ignore it """
                continue
            for i1 in range(i + 1, 9):
                if _sudoku[i1, j] == _sudoku[i, j]:
                    """ If row has same value, then error """
                    print('Invalid sudoku: positions', (i, j), (i1, j), 'have same value')
                    return False
            for j1 in range(j + 1, 9):
                if _sudoku[i, j1] == _sudoku[i, j]:
                    print('Invalid sudoku: positions', (i, j), (i, j1), 'have same value')
                    return False

            si = (i // 3) * 3
            sj = (j // 3) * 3
            for i1 in range(si, si + 3):
                for j1 in range(sj, sj + 3):
                    if _sudoku[i1, j1] == _sudoku[i, j] and (i, j) != (i1, j1):
                        print('Invalid sudoku: positions', (i, j), (i1, j1), 'have same value')
                        return False
    return True


def initial_random_sudoku():
    """ This function fills the diagonal squares randomly and returns the resultant sudoku """
    sudoku_ = np.zeros((9, 9), dtype=int)
    for s in range(3):
        values_ = sample(range(1, 10), k=9)
        for i in range(3):
            for j in range(3):
                """ Assign the sudoku using the random values """
                sudoku_[s * 3 + i, s * 3 + j] = values_[i * 3 + j]
    return sudoku_


def draw_sudoku(filename__, problem__, solution__=None):
    """ This function generates a image of the given sudoku problem, and outputs to the given filename,
        If solution is specified it fills the missing cells in the problem using the solution, assuming that
        solution have no missing cells.
    """
    problem__ = np.transpose(problem__)
    if solution__ is not None:
        solution__ = np.transpose(solution__)

    width, height = 500, 500
    """ Create a image of given dimensions """
    im = np.zeros((width, height, 3), dtype=np.uint8)
    """ Fill in the background color """
    for i in range(3):
        for j in range(3):
            color = (180, 180, 180) if (i + j) % 2 == 0 else (255, 255, 255)
            im = cv2.rectangle(im, (i * width // 3, j * height // 3), ((i + 1) * width // 3, (j + 1) * height // 3),
                               color, -1)
    """ Draw the grid """
    for i in range(10):
        im = cv2.line(im, (i * width // 9 - 1, 0), (i * width // 9 - 1, height), (0, 0, 0), 1 if i % 3 > 0 else 3)
        im = cv2.line(im, (0, i * height // 9 - 1), (width, i * height // 9 - 1), (0, 0, 0), 1 if i % 3 > 0 else 3)
    """ Draw the given problem and the solution """
    for i in range(9):
        for j in range(9):
            position__ = (i * width // 9 + width // 40, (j + 1) * height // 9 - height // 40)
            if problem__[i, j] > 0:
                cv2.putText(im, str(problem__[i, j]), position__, cv2.FONT_HERSHEY_COMPLEX,
                            1.5, (0, 0, 0), 2, cv2.LINE_AA)
            elif solution__ is not None:
                cv2.putText(im, str(solution__[i, j]), position__, cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 0, 0), 1, cv2.LINE_AA)
    """ Output it to given file name """
    cv2.imwrite(filename__, im)


def generate_sudoku():
    """ This function generates a random sudoku problem """
    """ Get a random sudoku with diagonals filled in """
    sudoku_ = initial_random_sudoku()
    """ Find some solution of the sudoku """
    _problem, _choices, _positions = pre_process_sudoku(sudoku_)
    _solution = solve_sudoku(_problem, _choices, _positions)
    """ Validate sudoku """
    assert validate_sudoku(_solution)
    """ Now remove values from few of the cells to generate the problem """
    _all_positions = sample([(i, j) for i in range(9) for j in range(9)], k=81)
    problem__ = _solution.copy()
    for index, _position in enumerate(_all_positions, 1):
        """ Remove the current position and check if sudoku still has a single solution, 
        if yes remove the position, else restore the position, and check with next position """
        value_ = problem__[_position]
        problem__[_position] = 0
        _problem, _choices, _positions = pre_process_sudoku(problem__.copy())
        if num_solution(_problem, _choices, _positions) > 1:
            """ Restore it, if more than one possible solution """
            problem__[_position] = value_

    """ Assert that problem has a single solution """
    _problem, _choices, _positions = pre_process_sudoku(problem__.copy())
    assert num_solution(_problem, _choices, _positions) == 1
    __solution = solve_sudoku(_problem, _choices, _positions)
    """ Assert that the initial solution and final solution are equal, 
    further proving that only one solution exits """
    assert np.all((_solution == __solution))
    return problem__, __solution


if __name__ == '__main__':
    """Generate 100 sudoku problems and their solutions into the 
    "problems/" and "solutions/" directory respectively"""
    for i in range(1, 101):
        print("Generating Problem: ", i)
        sudoku_problem, sudoku_solution = generate_sudoku()
        print_sudoku(sudoku_problem)
        draw_sudoku("problems/" + str(i) + '.png', sudoku_problem)
        draw_sudoku("solutions/" + str(i) + '.png', sudoku_problem, sudoku_solution)

