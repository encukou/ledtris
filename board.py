
CYAN = 0, 3, 2
BLUE = 0, 0, 4
ORANGE = 4, 2, 0
YELLOW = 3, 3, 0
LIME = 0, 3, 0
MAGENTA = 3, 0, 4
RED = 3, 0, 0


class Shape:
    def __init__(self, name, color, rows):
        self.name = name
        self.color = color
        self.size = len(rows)
        self.rotations = rotations = []
        blocks = frozenset(
            (x, y)
            for y, row in enumerate(rows)
            for x, char in enumerate(row)
            if char == 'X')
        for i in range(4):
            rotations.append(blocks)
            blocks = frozenset((self.size - 1 - y, x) for x, y in blocks)

    def __repr__(self):
        return "<{} '{}' at {}>".format(type(self).__name__, self.name,
                                        hex(id(self)))


class Piece:
    def __init__(self, board, shape):
        self.shape = shape
        self.board = board
        self.col = (self.board.width - self.shape.size) // 2
        self.row = -2
        self.rotation = 0

    def gen_blocks(self, dx, dy, dr):
        c = self.col + dx
        r = self.row + dy
        for x, y in self.shape.rotations[(self.rotation + dr) % 4]:
            yield x + c, y + r

    def crashed(self, dx, dy, dr):
        board = self.board
        blocks = board.blocks
        for xy in self.gen_blocks(dx, dy, dr):
            if xy in blocks:
                return True
            x, y = xy
            if x >= board.width or x < 0 or y >= board.height:
                return True
        return False

    def move(self, dx=0, dy=0, dr=0):
        if not self.crashed(dx, dy, dr):
            self.col += dx
            self.row += dy
            self.rotation += dr
            return True
        return False

    def set(self):
        blocks = self.board.blocks
        color = self.shape.color
        for x, y in self.gen_blocks(0, 0, 0):
            blocks[x, y] = color
        self.board = None

    def gen_shifts(self, direction):
        if self.shape.size == 4:
            x_shifts = 0, direction, -direction, direction * 2, -direction * 2
        else:
            x_shifts = 0, direction, -direction
        for x in x_shifts:
            for y in 0, 1:
                yield x, y

    def __repr__(self):
        return "<{} {} @ {},{} r{} at {}>".format(
            type(self).__name__,
            self.shape.name, self.col, self.row, self.rotation,
            hex(id(self)))


SHAPES = tuple(Shape(*args) for args in (
    ('I', CYAN, ('', 'XXXX', '', '')),
    ('J', BLUE, ('X', 'XXX', '')),
    ('L', ORANGE, ('  X', 'XXX', '')),
    ('O', YELLOW, ('XX', 'XX')),
    ('S', LIME, (' XX', 'XX', '')),
    ('T', MAGENTA, (' X ', 'XXX', '')),
    ('Z', RED, ('XX', ' XX')),
))

I, J, L, O, S, T, Z = SHAPES

class Board:
    def __init__(self, width, height, *, rng, shapes=None):
        self.width = width
        self.height = height
        self.rng = rng
        self.shapes = shapes or SHAPES

        self.blocks = {}
        self.piece_generator = self._generate_pieces()
        self.current = next(self.piece_generator)
        self.upcoming = next(self.piece_generator)
        self.clear_lines = None

    def _generate_pieces(self):
        while True:
            shapes = list(self.shapes)
            while shapes:
                idx = self.rng() % len(shapes)
                yield Piece(self, shapes[idx])
                del shapes[idx]

    def advance(self, *, left=0, right=0, cw=0, ccw=0, down=0,
                hard_drop=False):
        if self.clear_lines:
            for _ in self.clear_lines:
                pass
            self.clear_lines = None

        current = self.current

        rotation = cw - ccw
        if rotation:
            sign = 1 if rotation > 0 else -1
            for n in range(abs(rotation)):
                for dx, dy in current.gen_shifts(sign):
                    if current.move(dr=sign, dx=dx, dy=dy):
                        break
                else:
                    break

        sideways = right - left
        if sideways:
            sign = 1 if sideways > 0 else -1
            for n in range(abs(sideways)):
                current.move(dx=sign)

        if hard_drop:
            while current.move(dy=+1):
                pass
            down = 1

        for i in range(down):
            if not current.move(dy=+1):
                return True

        return False

    def get_cleared_lines(self):
        curr_blocks = set(self.current.gen_blocks(0, 0, 0))
        candidates = set(y for x, y in curr_blocks)
        width = self.width
        self_blocks = self.blocks
        lines = sorted((y for y in candidates
                        if all((x, y) in self_blocks or (x, y) in curr_blocks
                               for x in range(0, width))),
                       reverse=True)
        return lines

    def next_piece(self):
        cleared_lines = self.get_cleared_lines()
        self.current.set()
        self.current = self.upcoming
        self.upcoming = next(self.piece_generator)
        if cleared_lines:
            self.clear_lines = self._clear_lines(cleared_lines)
        return cleared_lines

    def gen_current_blocks(self):
        return self.current.gen_blocks(0, 0, 0)

    @property
    def current_color(self):
        return self.current.shape.color

    def _clear_lines(self, cleared):
        cleared = set(cleared)
        max_line = max(cleared)
        num_skip = 0
        delta = 0
        todo_count = len(cleared)
        for dest_line in range(max_line, -1, -1):
            while dest_line - delta in cleared:
                delta += 1
            source_line = dest_line - delta
            update = {}
            some_popped = 0
            for i in range(self.width):
                source_key = i, source_line
                dest_key = i, dest_line
                popped = self.blocks.pop(source_key, None)
                if popped:
                    some_popped = True
                    update[source_key] = None
                    update[dest_key] = popped
                    self.blocks[dest_key] = popped
                else:
                    dest_popped = self.blocks.pop(dest_key, None)
                    if dest_popped:
                        update[dest_key] = None
            if not some_popped:
                todo_count -= 1
            if not todo_count:
                return
            yield update
