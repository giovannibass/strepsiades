from board import Board
import pytest

def test_safe_square():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[0][0] = "r"
    board.squares[2][0] = "b"

    assert board.is_square_attacked(4, 0, "b") is False

def test_attacked_square():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[0][0] = "r"
    
    assert board.is_square_attacked(4, 0, "b") is True

def test_knight_attack():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[2][1] = "n"

    assert board.is_square_attacked(4, 2, "b") is True

def test_king_in_check():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[4][0] = "K"
    board.squares[0][0] = "r"

    assert board.is_in_check("w") is True

def test_king_is_safe():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[4][0] = "K"
    board.squares[2][0] = "B"
    board.squares[0][0] = "r"

    assert board.is_in_check("w") is False

def test_no_attack():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    
    assert board.is_square_attacked(4, 4, "b") is False

def test_board_edge():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[1][0] = "P"

    assert board.is_square_attacked(0, 1, "w") is True

def test_empty_no_check():
    board = Board()
    
    assert board.is_in_check("w") is False
    assert board.is_in_check("b") is False

def test_error_with_no_king():
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]

    with pytest.raises(ValueError):
        board.is_in_check("w")

def test_error_with_invalid_color():
    board = Board()

    with pytest.raises(ValueError):
        board.is_square_attacked(4, 4, "not_a_color")
