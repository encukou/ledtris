import pytest

import board

SHAPES = {letter: getattr(board, letter) for letter in 'IJLOSTZ'}

COLORS = {letter: shape.color for letter, shape in SHAPES.items()}
COLORS['X'] = 255, 255, 255

LETTERS = {color: letter for letter, color in COLORS.items()}
LETTERS[None] = ' '

class BoardFixture:
    def init(self, *rows, shapes='IJLOSTZ'):
        self.board = board.Board(len(rows[0]), len(rows), rng=lambda: 0)
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char != ' ':
                    self.board.blocks[x, y] = COLORS[char]
        self.debug_print()

    def debug_print(self):
        for y in range(self.board.height):
            print('[', end='')
            for x in range(self.board.width):
                print(LETTERS[self.board.blocks.get((x, y))], end='')
            print(']')

    def go(self, **kwargs):
        print('-' * self.board.width)
        if self.board.advance(**kwargs):
            self.board.next_piece()
        self.debug_print()

    def assert_situation(self, *rows):
        should = {}
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char != ' ':
                    should[(x, y)] = COLORS[char]
        assert self.board.blocks == should

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
