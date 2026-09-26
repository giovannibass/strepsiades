from board import Board
from move import Move
import pytest

def test_king_check():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[7][4] = "K"
    board.squares[6][4] = "R"
    board.squares[0][4] = "r"
    board.squares[0][0] = "k"

    # Testing that the board state is restored after generating legal moves
    before_squares = [row.copy() for row in board.squares]
    before_castling = board.castling_rights
    before_en_passant = board.en_passant_target
    before_history_length = len(board._history)
    before_halfmove = board.halfmove
    before_fullmove = board.fullmove

    legal_moves = board.generate_legal_moves()

    assert Move((6, 4), (6, 5)) not in legal_moves
    assert Move((6, 4), (5, 4)) in legal_moves
    assert board.side_to_move == "w"
    assert board.squares[6][4] == "R"
    
    # Testing restoration
    assert before_squares == board.squares
    assert before_castling == board.castling_rights
    assert before_en_passant == board.en_passant_target
    assert before_history_length == len(board._history)
    assert before_halfmove == board.halfmove
    assert before_fullmove == board.fullmove

def test_illegal_king_capture():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[7][0] = "R"
    board.squares[0][0] = "k"
    board.squares[7][7] = "K"
    legal_moves = board.generate_legal_moves()

    assert Move((7, 0), (0, 0)) not in legal_moves

def test_illegal_king_move():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[4][3] = "K"
    board.squares[0][4] = "r"
    board.squares[0][0] = "k"
    legal_moves = board.generate_legal_moves()

    assert Move((4, 3), (4, 4)) not in legal_moves

def test_check_is_blocked():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[7][4] = "K"
    board.squares[5][2] = "B"
    board.squares[6][0] = "P"
    board.squares[0][4] = "r"
    board.squares[0][0] = "k"
    legal_moves = board.generate_legal_moves()

    assert Move((5, 2), (3, 4)) in legal_moves
    assert Move((6, 0), (5, 0)) not in legal_moves

def test_black_to_move():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[1][4] = "r"
    board.squares[7][4] = "R"
    board.squares[0][4] = "k"
    board.squares[7][0] = "K"
    board.side_to_move = "b"
    legal_moves = board.generate_legal_moves()

    assert Move((1, 4), (1, 5)) not in legal_moves
    assert Move((1, 4), (2, 4)) in legal_moves

def test_no_king():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[7][0] = "R"
    board.squares[0][7] = "k"
    
    # Testing that the board state is restored after generating legal moves
    before_squares = [row.copy() for row in board.squares]
    before_castling = board.castling_rights
    before_en_passant = board.en_passant_target
    before_history_length = len(board._history)
    before_halfmove = board.halfmove
    before_fullmove = board.fullmove

    with pytest.raises(ValueError):
        board.generate_legal_moves()

    # Testing restoration
    assert before_squares == board.squares
    assert before_castling == board.castling_rights
    assert before_en_passant == board.en_passant_target
    assert before_history_length == len(board._history)
    assert before_halfmove == board.halfmove
    assert before_fullmove == board.fullmove
 
