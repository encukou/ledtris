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
            print(']', y)

    def go(self, **kwargs):
        print('-' * (self.board.width+2),
              'round {}:'.format(self.round_number),
              *('{}={}'.format(*item) for item in kwargs.items()))
        self.round_number += 1
        if self.board.advance(**kwargs):
            print('piece set:', self.board.current)
            self.board.next_piece()
        return self.board.clear_lines

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
        print('=' * (self.board.width+2), 'got:')
        self.debug_print()
        if got != should:
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
    board_fixture.go(ccw=1, down=2)
    board_fixture.assert_situation(
        '  ::    ',
        '   :    ',
        '   :    ',
        current_shape='L',
    )


def test_rotation_i1(board_fixture):
    board_fixture.init(
        'X         ',
        'XX        ',
        'XX        ',
        'XX        ',
        'X    X    ',
        'XX   X    ',
        'XX   XX   ',
        shapes='ILTS',
    )
    board_fixture.go(down=3, right=1)
    board_fixture.assert_situation(
        'X         ',
        'XX        ',
        'XX  ::::  ',
        'XX        ',
        'X    X    ',
        'XX   X    ',
        'XX   XX   ',
    )
    board_fixture.go(cw=1)
    board_fixture.assert_situation(
        'X         ',
        'XX    :   ',
        'XX    :   ',
        'XX    :   ',
        'X    X:   ',
        'XX   X    ',
        'XX   XX   ',
    )


def test_rotation_i2(board_fixture):
    board_fixture.init(
        'X         ',
        'XX        ',
        'XX        ',
        'XX        ',
        'X    X X  ',
        'XX   X XX ',
        'XX   XX X ',
        shapes='ILTS',
    )
    board_fixture.go(down=3, right=1)
    board_fixture.assert_situation(
        'X         ',
        'XX        ',
        'XX  ::::  ',
        'XX        ',
        'X    X X  ',
        'XX   X XX ',
        'XX   XX X ',
    )
    board_fixture.go(cw=1)
    board_fixture.assert_situation(
        'X         ',
        'XX    :   ',
        'XX    :   ',
        'XX    :   ',
        'X    X:X  ',
        'XX   X XX ',
        'XX   XX X ',
    )


def test_rotation_i3(board_fixture):
    board_fixture.init(
        'X         ',
        'XX        ',
        'XX        ',
        'XX        ',
        'X   XX X  ',
        'XX  X  XX ',
        'XX  X   X ',
        shapes='ILTS',
    )
    board_fixture.go(down=3, right=1)
    board_fixture.assert_situation(
        'X         ',
        'XX        ',
        'XX  ::::  ',
        'XX        ',
        'X   XX X  ',
        'XX  X  XX ',
        'XX  X   X ',
    )
    board_fixture.go(cw=1)
    board_fixture.assert_situation(
        'X         ',
        'XX    :   ',
        'XX    :   ',
        'XX    :   ',
        'X   XX:X  ',
        'XX  X  XX ',
        'XX  X   X ',
    )

def test_cleared_one(board_fixture):
    board_fixture.init(
        'XX    XX',
        'XX    XX',
        shapes='ILT',
    )
    board_fixture.go(down=2)
    board_fixture.assert_situation(
        'XX    XX',
        'XX::::XX',
    )
    assert board_fixture.board.get_cleared_lines() == [1]

def test_cleared_four(board_fixture):
    board_fixture.init(
        '    X X ',
        'XXX XXXX',
        'XXX XXXX',
        'XXX XXXX',
        'XXX XXXX',
        '   X    ',
        shapes='ILT',
    )
    board_fixture.go(down=3, cw=1)
    board_fixture.assert_situation(
        '    X X ',
        'XXX:XXXX',
        'XXX:XXXX',
        'XXX:XXXX',
        'XXX:XXXX',
        '   X    ',
    )
    assert board_fixture.board.get_cleared_lines() == [4, 3, 2, 1]
    it = board_fixture.go(down=1)
    board_fixture.assert_situation(
        '    X X ',
        'XXXIXXXX',
        'XXXIXXXX',
        'XXXIXXXX',
        'XXXIXXXX',
        '   X    ',
    )
    next(it)
    board_fixture.assert_situation(
        '        ',
        'XXXIXXXX',
        'XXXIXXXX',
        'XXXIXXXX',
        '    X X ',
        '   X    ',
    )
    next(it)
    board_fixture.assert_situation(
        '        ',
        'XXXIXXXX',
        'XXXIXXXX',
        '        ',
        '    X X ',
        '   X    ',
    )
    next(it)
    board_fixture.assert_situation(
        '        ',
        'XXXIXXXX',
        '        ',
        '        ',
        '    X X ',
        '   X    ',
    )
    next(it)
    board_fixture.assert_situation(
        '       ',
        '       ',
        '       ',
        '       ',
        '    X X ',
        '   X    ',
    )
    with pytest.raises(StopIteration):
        next(it)
    board_fixture.assert_situation(
        '        ',
        '        ',
        '        ',
        '        ',
        '    X X ',
        '   X    ',
    )

@pytest.mark.parametrize('play_out', [True, False])
def test_clear_complex(board_fixture, play_out):
    board_fixture.init(
        '        ',
        'XXX     ',
        'XXX  XXX',
        'XXX  XXX',
        'XXX XXXX',
        '   X    ',
        shapes='JIT',
    )
    board_fixture.go(down=1)
    board_fixture.assert_situation(
        '  :::   ',
        'XXX     ',
        'XXX  XXX',
        'XXX  XXX',
        'XXX XXXX',
        '   X    ',
    )
    board_fixture.go(down=1, cw=1)
    board_fixture.assert_situation(
        '   ::   ',
        'XXX:    ',
        'XXX: XXX',
        'XXX  XXX',
        'XXX XXXX',
        '   X    ',
    )
    board_fixture.go(down=2)
    board_fixture.assert_situation(
        '        ',
        'XXX     ',
        'XXX::XXX',
        'XXX: XXX',
        'XXX:XXXX',
        '   X    ',
    )
    assert board_fixture.board.get_cleared_lines() == [4, 2]
    it = board_fixture.go(down=1)
    if play_out:
        board_fixture.assert_situation(
            '        ',
            'XXX     ',
            'XXXJJXXX',
            'XXXJ XXX',
            'XXXJXXXX',
            '   X    ',
        )
        next(it)
        board_fixture.assert_situation(
            '        ',
            'XXX     ',
            'XXXJJXXX',
            '        ',
            'XXXJ XXX',
            '   X    ',
        )
        next(it)
        board_fixture.assert_situation(
            '        ',
            '        ',
            'XXXJJXXX',
            'XXX     ',
            'XXXJ XXX',
            '   X    ',
        )
        next(it)
        board_fixture.assert_situation(
            '        ',
            '        ',
            '        ',
            'XXX     ',
            'XXXJ XXX',
            '   X    ',
        )
        with pytest.raises(StopIteration):
            next(it)
    else:
        it = board_fixture.go()
    board_fixture.assert_situation(
        '        ',
        '        ',
        '        ',
        'XXX     ',
        'XXXJ XXX',
        '   X    ',
    )
