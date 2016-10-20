import pytest

import board

SHAPES = {letter: getattr(board, letter) for letter in 'IJLOSTZ'}

COLORS = {letter: shape.color for letter, shape in SHAPES.items()}
COLORS['X'] = 255, 255, 255
COLORS[':'] = -1, -1, -1

LETTERS = {color: letter for letter, color in COLORS.items()}
LETTERS[None] = ' '

class BoardFixture:
    def init(self, *rows, shapes='IJLOSTZ'):
        self.round_number = 0
        self.board = board.Board(len(rows[0]), len(rows), rng=lambda: 0,
                                 shapes=[SHAPES[s] for s in shapes])
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char != ' ':
                    self.board.blocks[x, y] = COLORS[char]
        self.debug_print()

    def debug_print(self, blocks=None, current='_none'):
        if blocks is None:
            blocks = self.board.blocks
        if current is '_none':
            current = set(self.board.current.gen_blocks(0,0,0))
        for y in range(self.board.height):
            print('[', end='')
            for x in range(self.board.width):
                if (x, y) in current:
                    print(':', end='')
                else:
                    print(LETTERS[blocks.get((x, y))], end='')
            print(']')

    def go(self, **kwargs):
        print('-' * (self.board.width+2),
              'round {}:'.format(self.round_number),
              *('{}={}'.format(*item) for item in kwargs.items()))
        self.round_number += 1
        if self.board.advance(**kwargs):
            print('piece set:', self.board.current)
            self.board.next_piece()
        self.debug_print()

    def assert_situation(self, *rows, current_shape=None):
        if current_shape:
            assert self.board.current.shape is SHAPES[current_shape]
        should = {}
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char != ' ':
                    should[(x, y)] = COLORS[char]
        got = dict(self.board.blocks)
        got.update({(x, y): COLORS[':']
                    for x, y in self.board.gen_current_blocks()
                    if y >= 0})
        print('=' * (self.board.width+2), 'expected:')
        self.debug_print(blocks=should, current=())
        assert got == should

@pytest.fixture
def board_fixture():
    return BoardFixture()


def test_drop_i(board_fixture):
    board_fixture.init(
        '        ',
        'XXXXXXX ',
        'XXXXXXX ',
        shapes='ILT',
    )
    board_fixture.go(down=5)
    board_fixture.assert_situation(
        '  IIII  ',
        'XXXXXXX ',
        'XXXXXXX ',
    )


def test_left2_drop_i(board_fixture):
    board_fixture.init(
        '        ',
        'XXXXXXX ',
        'XXXXXXX ',
        shapes='ILT',
    )
    board_fixture.go(left=2, down=5)
    board_fixture.assert_situation(
        'IIII    ',
        'XXXXXXX ',
        'XXXXXXX ',
    )


def test_right2_drop_i(board_fixture):
    board_fixture.init(
        '        ',
        'XXXXXXX ',
        'XXXXXXX ',
        shapes='ILT',
    )
    board_fixture.go(right=2, down=5)
    board_fixture.assert_situation(
        '    IIII',
        'XXXXXXX ',
        'XXXXXXX ',
    )


def test_right3_drop_i(board_fixture):
    board_fixture.init(
        '        ',
        'XXXXXXX ',
        'XXXXXXX ',
        shapes='ILT',
    )
    board_fixture.go(right=3, down=5)
    board_fixture.assert_situation(
        '    IIII',
        'XXXXXXX ',
        'XXXXXXX ',
        current_shape='L',
    )


def test_drop_two(board_fixture):
    board_fixture.init(
        '        ',
        '        ',
        '        ',
        'XXXXXXX ',
        'XXXXXXX ',
        shapes='ILT',
    )
    board_fixture.go(down=5)
    board_fixture.go(down=5)
    board_fixture.assert_situation(
        '    L   ',
        '  LLL   ',
        '  IIII  ',
        'XXXXXXX ',
        'XXXXXXX ',
        current_shape='T',
    )


def test_rotation(board_fixture):
    board_fixture.init(
        '        ',
        '        ',
        '        ',
        shapes='LTS',
    )
    board_fixture.go(cw=1, down=1)
    board_fixture.assert_situation(
        '  ::    ',
        '   :    ',
        '   :    ',
        current_shape='L',
    )
