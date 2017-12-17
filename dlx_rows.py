import math


def build_blank_board():
    return [[0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9]


def dlx_row_to_rcv(dlxrow):
    """Pull (row,col,val) out from an encoded DLX list."""

    rowcol = dlxrow[0]
    rownum = dlxrow[1]

    row, col = decode(rowcol)
    ignore, num = decode(rownum)

    return row, col, num + 1


def decode(lst):
    """Take a list of 81 values with a single 1, decode two values out of its
    position. Return them in a tuple (major,minor)."""

    position = lst
    minor = position % 9
    major = position / 9
    return major, minor


def dlx_rows(list_of_lists):

    output_matrix = []

    for row in range(0, 9):
        for col in range(0, 9):
            output_matrix += list_to_dlx_row(row, col, list_of_lists[row][col])

    return output_matrix


def list_to_dlx_row(row, col, val):

    if val in range(1, 10):
        return [dlx_row(row, col, val)]
    else:
        return [dlx_row(row, col, value) for value in range(1, 10)]


def dlx_row(row, col, val):

    n_cols = 4*81
    output_row = [0]*n_cols
    val -= 1
    box = 3*math.floor(row/3) + math.floor(col/3)

    output_row[0*81 + 9*row + col] = 1
    output_row[1*81 + 9*row + val] = 1
    output_row[2*81 + 9*col + val] = 1
    output_row[3*81 + 9*box + val] = 1

    return output_row
