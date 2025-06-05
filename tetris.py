import curses
import random
import time

# Game configuration
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TICK_RATE = 0.5

SHAPES = {
    'I': [
        [(0,1), (1,1), (2,1), (3,1)],
        [(2,0), (2,1), (2,2), (2,3)]
    ],
    'J': [
        [(0,0), (0,1), (1,1), (2,1)],
        [(1,0), (2,0), (1,1), (1,2)],
        [(0,1), (1,1), (2,1), (2,2)],
        [(1,0), (1,1), (1,2), (0,2)]
    ],
    'L': [
        [(2,0), (0,1), (1,1), (2,1)],
        [(1,0), (1,1), (1,2), (2,2)],
        [(0,1), (1,1), (2,1), (0,2)],
        [(0,0), (1,0), (1,1), (1,2)]
    ],
    'O': [
        [(1,0), (2,0), (1,1), (2,1)]
    ],
    'S': [
        [(1,1), (2,1), (0,2), (1,2)],
        [(1,0), (1,1), (2,1), (2,2)]
    ],
    'T': [
        [(1,0), (0,1), (1,1), (2,1)],
        [(1,0), (1,1), (2,1), (1,2)],
        [(0,1), (1,1), (2,1), (1,2)],
        [(1,0), (0,1), (1,1), (1,2)]
    ],
    'Z': [
        [(0,1), (1,1), (1,2), (2,2)],
        [(2,0), (1,1), (2,1), (1,2)]
    ]
}

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rot = 0
        self.x = BOARD_WIDTH // 2 - 2
        self.y = 0
    @property
    def cells(self):
        return SHAPES[self.shape][self.rot]

    def rotate(self, board):
        next_rot = (self.rot + 1) % len(SHAPES[self.shape])
        if not self.collides(board, self.x, self.y, next_rot):
            self.rot = next_rot

    def collides(self, board, x, y, rot=None):
        if rot is None:
            rot = self.rot
        for cx, cy in SHAPES[self.shape][rot]:
            bx = x + cx
            by = y + cy
            if bx < 0 or bx >= BOARD_WIDTH or by < 0 or by >= BOARD_HEIGHT:
                return True
            if board[by][bx]:
                return True
        return False

    def imprint(self, board):
        for cx, cy in self.cells:
            board[self.y + cy][self.x + cx] = self.shape

def new_board():
    return [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def clear_lines(board):
    new_board_rows = [row for row in board if any(cell is None for cell in row)]
    lines_cleared = BOARD_HEIGHT - len(new_board_rows)
    while len(new_board_rows) < BOARD_HEIGHT:
        new_board_rows.insert(0, [None for _ in range(BOARD_WIDTH)])
    return new_board_rows, lines_cleared

def draw_board(stdscr, board, piece, score):
    stdscr.clear()
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            cell = board[y][x]
            char = '[]' if cell else ' .'
            stdscr.addstr(y, x*2, char)
    for cx, cy in piece.cells:
        stdscr.addstr(piece.y + cy, (piece.x + cx)*2, '[]')
    stdscr.addstr(0, BOARD_WIDTH*2 + 2, f"Score: {score}")
    stdscr.refresh()

def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    board = new_board()
    piece = Piece(random.choice(list(SHAPES.keys())))
    score = 0
    last_tick = time.time()
    while True:
        ch = stdscr.getch()
        if ch == curses.KEY_LEFT and not piece.collides(board, piece.x-1, piece.y):
            piece.x -= 1
        elif ch == curses.KEY_RIGHT and not piece.collides(board, piece.x+1, piece.y):
            piece.x += 1
        elif ch == curses.KEY_DOWN and not piece.collides(board, piece.x, piece.y+1):
            piece.y += 1
        elif ch == ord('q'):
            break
        elif ch == curses.KEY_UP:
            piece.rotate(board)
        if time.time() - last_tick > TICK_RATE:
            last_tick = time.time()
            if not piece.collides(board, piece.x, piece.y+1):
                piece.y += 1
            else:
                piece.imprint(board)
                board, lines = clear_lines(board)
                score += lines
                piece = Piece(random.choice(list(SHAPES.keys())))
                if piece.collides(board, piece.x, piece.y):
                    draw_board(stdscr, board, piece, score)
                    stdscr.addstr(BOARD_HEIGHT//2, BOARD_WIDTH - 4, 'GAME OVER')
                    stdscr.nodelay(0)
                    stdscr.getch()
                    break
        draw_board(stdscr, board, piece, score)

if __name__ == '__main__':
    curses.wrapper(game_loop)
