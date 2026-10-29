from board import Board
from evaluation import evaluate
import pytest

def test_evaluate():
    # Confirm that material score doesn't change with active color
    board = Board()
    board.load_fen("4k3/8/8/8/4P3/8/8/4K3 w - - 0 1")
    
    # White's turn. Extra white pawn
    assert evaluate(board) == 100

    # Same position, black's turn
    board.load_fen("4k3/8/8/8/4P3/8/8/4K3 b - - 0 1")
    assert evaluate(board) == 100
    
    # White's turn. Extra black pawn
    board.load_fen("4k3/8/8/8/4p3/8/8/4K3 w - - 0 1")
    assert evaluate(board) == -100

    # Same position, black's turn
    board.load_fen("4k3/8/8/8/4p3/8/8/4K3 b - - 0 1")
    assert evaluate(board) == -100
    
    # Material should be 0 with a king only board. White's turn
    board.load_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert evaluate(board) == 0

    # Black's turn
    board.load_fen("4k3/8/8/8/8/8/8/4K3 b - - 0 1")
    assert evaluate(board) == 0

    # Material should be 0 when balanced. White's turn
    board.load_fen("4k3/8/4P3/8/8/4p3/8/4K3 w - - 0 1")
    assert evaluate(board) == 0

    # Black's turn
    board.load_fen("4k3/8/4P3/8/8/4p3/8/4K3 b - - 0 1")
    assert evaluate(board) == 0

    # Calling upon the evaluate function doesn't change the board.
    before_squares = [row.copy() for row in board.squares]
    before_castling = board.castling_rights
    before_en_passant = board.en_passant_target
    before_history = board._history.copy()
    before_halfmove = board.halfmove
    before_fullmove = board.fullmove
    before_side_to_move = board.side_to_move

    evaluate(board)

    # Testing restoration
    assert before_squares == board.squares
    assert before_castling == board.castling_rights
    assert before_en_passant == board.en_passant_target
    assert before_history == board._history
    assert before_halfmove == board.halfmove
    assert before_fullmove == board.fullmove
    assert before_side_to_move == board.side_to_move
