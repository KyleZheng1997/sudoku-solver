from dlx_matrix import *
from dlx_rows import *
from dlx import DLX


class SudokuPuzzle(object):
    """Representation of a Sudoku puzzle, with methods to convert back and forth
    from an instance of DLX."""

    def __init__(self, squares):
        """Squares is a nested list representing an initial sudoku board. A 0
        represents an empty square, while a nonzero digit represents a square
        filled with that value."""

        self.dlxrows = squares
        self.sparseMatrix = SparseMatrix(self.dlxrows)

        self.dlx = DLX(self.sparseMatrix)

    def solve(self):
        """Solve the sudoku puzzle. Return value is a nested list in the same
        format as the input to the constructor."""
        self.dlx_soln = self.dlx.search()

        if self.dlx_soln:
            self.soln_rows = [node.rowindex for node in self.dlx_soln if node]
        else:
            return None

        dlx_encoded_soln = [self.sparseMatrix.colindices_for(row) for row in self.soln_rows]
        rcvs = map(dlx_row_to_rcv, dlx_encoded_soln)

        out = build_blank_board()

        for row, col, val in rcvs:
            out[int(row)][int(col)] = val

        return out
