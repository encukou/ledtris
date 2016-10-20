
CYAN = 0, 3, 2
BLUE = 0, 0, 4
ORANGE = 4, 2, 0
YELLOW = 3, 3, 0
LIME = 0, 3, 0
MAGENTA = 3, 0, 4
RED = 3, 0, 0

BLACK = 0, 0, 0
WHITE = 3, 3, 3
FLASH = 255, 255, 255


class Shape:
    def __init__(self, color, rows):
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
            blocks = frozenset((self.size - y, x) for x, y in blocks)


class Piece:
    def __init__(self, board, shape):
        self.shape = shape
        self.board = board
        self.col = 0
        self.row = 0
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
        yield 0, 0
        r = self.rotation
        for val in SHIFTS.get((self.shape.size, r, (r + direction) % 4), ()):
            y, x = divmod(val, 8)
            if x > 4:
                x -= 8
                y += 1
            yield x, -y


SHAPES = tuple(Shape(*args) for args in (
    (CYAN, ('', 'XXXX', '', '')),
    (BLUE, ('X', 'XXX', '')),
    (ORANGE, ('  X', 'XXX', '')),
    (YELLOW, ('XX', 'XX')),
    (LIME, (' XX', 'XX', '')),
    (MAGENTA, (' X ', 'XXX', '')),
    (RED, ('XX', ' XX')),
))

SHIFTS = {
    # http://web.archive.org/web/20080226183843/http://www.the-shell.net/img/srs_study.html
    (4, 0, 1): (+2, -1, +10, -17),
    (4, 0, 3): (-2, +1, +6, -15),
    (4, 1, 2): (-2, +1, +6, +7),
    (4, 1, 0): (-2, +1, +17, -10),
    (4, 2, 3): (+1, -2, +17, -10),
    (4, 2, 1): (-1, +2, +15, -6),
    (4, 3, 0): (+2, -1, +15, -6),
    (4, 3, 2): (+2, -1, +10, -9),

    (3, 0, 1): (+1, -7, +16, +17),
    (3, 0, 4): (-1, -9, +16, +15),
    (3, 1, 2): (-1, +7, -16, -17),
    (3, 1, 0): (-1, +7, -16, -17),
    (3, 2, 3): (-1, -9, +16, +15),
    (3, 2, 1): (+1, -7, +16, +17),
    (3, 3, 0): (+1, +9, -16, -15),
    (3, 3, 2): (+1, +9, -16, -15),
}


class Board:
    def __init__(self, width, height, rng):
        self.width = width
        self.height = height
        self.rng = rng
        self.piece_generator = self._generate_pieces()
        self.current = next(self.piece_generator)
        self.upcoming = next(self.piece_generator)
        self.blocks = {}

    def _generate_pieces(self):
        while True:
            shapes = list(SHAPES)
            while shapes:
                idx = self.rng() % len(shapes)
                yield Piece(self, shapes[idx])
                del shapes[idx]

    def advance(self, *, left=0, right=0, cw=0, ccw=0, ticks=0,
                hard_drop=False):
        current = self.current

        rotation = ccw - cw
        if rotation:
            sign = 1 if rotation > 0 else -1
            for n in range(abs(rotation)):
                for dx, dy in current.gen_shifts(sign):
                    if current.move(dr=sign, dx=dx, dy=dy):
                        break
                else:
                    break

        for i in range(left):
            current.move(dx=-1)
        for i in range(right):
            current.move(dx=+1)

        if hard_drop:
            while current.move(dy=+1):
                pass
            ticks = 1

        for i in range(ticks):
            if not current.move(dy=+1):
                return True

        return False

    def next_piece(self):
        self.current.set()
        self.current = self.upcoming
        self.upcoming = next(self.piece_generator)

    def gen_current_blocks(self):
        return self.current.gen_blocks(0, 0, 0)

    @property
    def current_color(self):
        return self.current.shape.color
