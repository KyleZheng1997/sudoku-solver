import math


class SparseMatrix(object):
    """The matrix from which we'll be picking out columns to solve the set-cover
    problem, for DLX."""

    def __init__(self, rows):
        """Takes a list of rows, each of which is a list of 0s and 1s."""

        self.node_table = {}
        self.rows = rows
        self.r_index = 0
        nRow = 0
        nCol = 0

        for row in rows:
            nCol = 0
            for col in row:
                box = 3*math.floor(nRow/3) + math.floor(nCol/3)
                if col in range(1, 10):
                    val = col - 1

                    self.node_table[(self.r_index, 0*81 + 9*nRow + nCol)] = Node(self.r_index, 0*81 + 9*nRow + nCol)
                    self.node_table[(self.r_index, 1*81 + 9*nRow + val)]  = Node(self.r_index, 1*81 + 9*nRow + val)
                    self.node_table[(self.r_index, 2*81 + 9*nCol + val)]  = Node(self.r_index, 2*81 + 9*nCol + val)
                    self.node_table[(self.r_index, 3*81 + 9*box + val)]   = Node(self.r_index, 3*81 + 9*box + val)
                    self.r_index += 1
                else:
                    for i in range(0, 9):
                        val = i
                        self.node_table[(self.r_index, 0*81 + 9*nRow + nCol)] = Node(self.r_index, 0*81 + 9*nRow + nCol)
                        self.node_table[(self.r_index, 1*81 + 9*nRow + val)]  = Node(self.r_index, 1*81 + 9*nRow + val)
                        self.node_table[(self.r_index, 2*81 + 9*nCol + val)]  = Node(self.r_index, 2*81 + 9*nCol + val)
                        self.node_table[(self.r_index, 3*81 + 9*box + val)]   = Node(self.r_index, 3*81 + 9*box + val)
                        self.r_index += 1
                nCol += 1
            nRow += 1

        self.r_index -= 1

        self.build_columns()
        self.link_columns()
        self.link_nodes()

    def build_columns(self):
        """Put all the columns that this matrix has into self.columns. Note that a
        column can be empty of nodes."""

        colindices = range(0, 324)

        self.columns = [Column(index) for index in colindices]
        self.column_table = {}
        self.column_header = Column('h', header=1)
        self.columns.append(self.column_header)

        for col in self.columns:
            self.column_table[col.name] = col

    def link_columns(self):
        prev = None
        first = None

        for column in self.columns:
            if not first:
                first = column
            elif prev:
                column.left = prev
                prev.right = column
            prev = column

        column.right = first
        first.left = column

    def link_nodes(self):
        """Link all the nodes in the matrix together."""

        self.link_nodes_in_rows()
        self.link_nodes_in_columns()

    def link_nodes_in_rows(self):
        """For each row, make the circular linked-list of those nodes."""
        rowindices = self.rowindices()

        for r in rowindices:
            colindices = self.colindices_for(r)

            prev = None
            first = None
            for c in colindices:
                node = self.node_table[(r,c)]

                if not first:
                    first = node
                elif prev:
                    node.left = prev
                    prev.right = node
                prev = node

            node.right = first
            first.left = node

    def link_nodes_in_columns(self):
        """For each column, make the circular linked-list of those nodes, with
        column header objects in the loop."""
        colindices = self.colindices()

        for c in colindices:
            column = self.column_table[c]
            rowindices = self.rowindices_for(c)
            column.size = len(rowindices)

            prev = None
            first = None
            for r in rowindices:
                node = self.node_table[(r,c)]
                node.column = column

                if not first:
                    first = node
                elif prev:
                    node.up = prev
                    prev.down = node
                prev = node

                column.up = node
                node.down = column

                column.down = first
                first.up = column

    def colindices(self):
        keys = self.node_table.keys()

        colindices = [colindex for (rowindex,colindex) in keys]
        colindices = list(set(colindices))
        colindices.sort()

        return colindices

    def rowindices(self):
        keys = self.node_table.keys()

        rowindices = [rowindex for (rowindex,colindex) in keys]
        rowindices = list(set(rowindices))
        rowindices.sort()

        return rowindices

    def colindices_for(self, r):
        """Take a given row index and return the list of the columns with nodes on
        that row."""

        keys = self.node_table.keys()

        colindices = [colindex for (rowindex,colindex) in keys if rowindex == r]
        colindices = list(set(colindices))
        colindices.sort()

        return colindices

    def rowindices_for(self, c):
        """Take a given column index and return the list of the rows with nodes on
        that column."""

        keys = self.node_table.keys()

        rowindices = [rowindex for (rowindex,colindex) in keys if colindex == c]
        rowindices.sort()

        return rowindices

    def cover(self, column):
        """Remove a column; we can put it back in later. Parameter /column/ is the
        actual column object."""

        column.right.left = column.left
        column.left.right = column.right

        rowstart = column.down
        while rowstart != column:

            node = rowstart.right

            while node != rowstart:
                node.down.up = node.up
                node.up.down = node.down
                node.column.size -= 1

                node = node.right

            rowstart = rowstart.down

    def uncover(self, column):
        """Put a column back in. /column/ is the actual column object."""

        rowstart = column.up
        while rowstart != column:

            node = rowstart.left

            while node != rowstart:
                node.column.size += 1
                node.down.up = node
                node.up.down = node

                node = node.left

            rowstart = rowstart.up

        column.right.left = column
        column.left.right = column


class Node(object):
    def __init__(self, rowindex, colindex):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = None

        self.rowindex = rowindex
        self.colindex = colindex

    def __repr__(self):
        return "[node %d,%d]" % (self.rowindex, self.colindex)


class Column(object):
    def __init__(self, name, header=0):
        self.size = 0
        self.up = self
        self.down = self
        self.left = None
        self.right = None
        self.name = name
        self.isheader = header

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "col " + str(self.name)
