"""Connect 4 rules + minimax (negamax) AI with alpha-beta pruning."""
import time

ROWS, COLS = 6, 7
EMPTY, HUMAN, AI = 0, 1, 2
WIN_SCORE = 100_000
# Search from the centre outwards: better move ordering => more alpha-beta cutoffs.
COL_ORDER = sorted(range(COLS), key=lambda c: abs(c - COLS // 2))
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))


def other(p):
    return HUMAN if p == AI else AI


# ---------------------------------------------------------------- rules
def new_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]  # row 0 = top, row 5 = bottom


def valid_cols(b):
    return [c for c in COL_ORDER if b[0][c] == EMPTY]


def drop(b, col, p):
    """Place a piece; returns the row it landed in."""
    for r in range(ROWS - 1, -1, -1):
        if b[r][col] == EMPTY:
            b[r][col] = p
            return r
    raise ValueError("column full")


def undo(b, r, c):
    b[r][c] = EMPTY


def winning_line(b, r, c):
    """Return the 4+ connected cells through (r, c), or None."""
    p = b[r][c]
    for dr, dc in DIRS:
        line = [(r, c)]
        for sign in (1, -1):
            rr, cc = r + dr * sign, c + dc * sign
            while 0 <= rr < ROWS and 0 <= cc < COLS and b[rr][cc] == p:
                line.append((rr, cc))
                rr, cc = rr + dr * sign, cc + dc * sign
        if len(line) >= 4:
            return line
    return None


class Game:
    """Turn-based game loop: validates moves, switches turns, detects win/draw."""

    def __init__(self, ai_first=False, depth=5):
        self.board = new_board()
        self.turn = AI if ai_first else HUMAN
        self.depth = depth
        self.status = "playing"  # playing | win | draw
        self.winner = None
        self.win_cells = []
        self.last_ai_stats = None

    def play(self, col, p):
        if self.status != "playing":
            raise ValueError("game is over")
        if p != self.turn:
            raise ValueError("not your turn")
        if not (0 <= col < COLS) or self.board[0][col] != EMPTY:
            raise ValueError("invalid move")
        r = drop(self.board, col, p)
        line = winning_line(self.board, r, col)
        if line:
            self.status, self.winner, self.win_cells = "win", p, line
        elif not valid_cols(self.board):
            self.status = "draw"
        else:
            self.turn = other(p)
        return r

    def ai_move(self):
        col, stats = best_move(self.board, AI, self.depth)
        self.last_ai_stats = stats
        self.play(col, AI)
        return col

    def to_dict(self):
        return {"board": self.board, "turn": self.turn, "status": self.status,
                "winner": self.winner, "win_cells": self.win_cells,
                "ai": self.last_ai_stats}


# ---------------------------------------------------------------- AI
def _score_window(w, p):
    mine, theirs, empty = w.count(p), w.count(other(p)), w.count(EMPTY)
    if mine and theirs:
        return 0
    if mine == 3 and empty == 1: return 5    # one move from winning
    if mine == 2 and empty == 2: return 2    # developing line
    if theirs == 3 and empty == 1: return -6  # must-block threat (weighted higher)
    if theirs == 2 and empty == 2: return -2
    return 0


def evaluate(b, p):
    """Heuristic score of a non-terminal position from p's point of view.

    Weighs: (1) centre-column control (a centre piece sits in the most
    possible 4-windows) and (2) open 2s/3s in every horizontal, vertical and
    diagonal window, penalising the opponent's threats slightly more.
    """
    score = sum(3 for r in range(ROWS) if b[r][COLS // 2] == p)
    score -= sum(3 for r in range(ROWS) if b[r][COLS // 2] == other(p))
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in DIRS:
                er, ec = r + 3 * dr, c + 3 * dc
                if 0 <= er < ROWS and 0 <= ec < COLS:
                    score += _score_window([b[r + i * dr][c + i * dc] for i in range(4)], p)
    return score


class _Stats:
    nodes = 0
    pruned = 0


def _negamax(b, depth, alpha, beta, p, last, st):
    st.nodes += 1
    if last and b[last[0]][last[1]] == other(p) and winning_line(b, *last):
        return -(WIN_SCORE + depth)  # opponent just won; sooner wins score higher
    moves = valid_cols(b)
    if not moves:
        return 0
    if depth == 0:
        return evaluate(b, p)
    best = -float("inf")
    for c in moves:
        r = drop(b, c, p)
        score = -_negamax(b, depth - 1, -beta, -alpha, other(p), (r, c), st)
        undo(b, r, c)
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:  # opponent already has a better option elsewhere
            st.pruned += 1
            break
    return best


def best_move(b, p, depth):
    st, start = _Stats(), time.perf_counter()
    best_col, best_score, alpha = None, -float("inf"), -float("inf")
    for c in valid_cols(b):
        r = drop(b, c, p)
        score = -_negamax(b, depth - 1, -float("inf"), -alpha, other(p), (r, c), st)
        undo(b, r, c)
        if score > best_score:
            best_col, best_score = c, score
        alpha = max(alpha, score)
    return best_col, {"column": best_col, "depth": depth, "score": best_score,
                      "nodes": st.nodes, "pruned": st.pruned,
                      "ms": round((time.perf_counter() - start) * 1000)}
