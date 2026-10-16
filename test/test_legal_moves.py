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

def test_castle1():
    # Checking if castling moves are included in the legal move list
    board = Board()
    # Creating empty board
    board.squares = [["."] * 8 for x in range(8)]
    board.squares[7][4] = "K"
    board.squares[7][7] = "R"
    board.squares[7][0] = "R"
    board.squares[0][4] = "k"
    board.squares[0][7] = "r"
    board.squares[0][0] = "r"
    board.castling_rights = "KQkq"
    legal_moves = board.generate_legal_moves()

    # Assert that white can castle in both directions
    assert Move((7, 4), (7, 6), is_castling=True) in legal_moves
    assert Move((7, 4), (7, 2), is_castling=True) in legal_moves

    # Assert that white can't castle with a missing rook
    board.squares[7][7] = "."
    legal_moves = board.generate_legal_moves()
    assert Move((7, 4), (7, 6), is_castling=True) not in legal_moves
    board.squares[7][7] = "R"

    # Assert that castling can't occur with the king in check
    board.squares[4][4] = "q"
    legal_moves = board.generate_legal_moves()
    assert Move((7, 4), (7, 6), is_castling=True) not in legal_moves
    board.squares[4][4] = "."

    # Assert that castling can't occur when a square the king will cross is attacked
    board.squares[4][5] = "q"
    legal_moves = board.generate_legal_moves()
    assert Move((7, 4), (7, 6), is_castling=True) not in legal_moves
    board.squares[4][5] = "."

    # Assert that castling can't occur when destination square is attacked
    board.squares[4][6] = "q"
    legal_moves = board.generate_legal_moves()
    assert Move((7, 4), (7, 6), is_castling=True) not in legal_moves
    board.squares[4][6] = "."

    # Assert white can't castle if castling rights are gone
    board.castling_rights = "kq"
    legal_moves = board.generate_legal_moves()
    assert Move((7, 4), (7, 6), is_castling=True) not in legal_moves
    board.castling_rights = "KQkq"

    # Make sure Black doesn't get White's kingside/queenside castling as a move
    board.side_to_move = "b"
    legal_moves = board.generate_legal_moves()
    assert Move((7, 4), (7, 6), is_castling=True) not in legal_moves
    assert Move((7, 4), (7, 2), is_castling=True) not in legal_moves

    # Assert that black can castle in both directions
    assert Move((0, 4), (0, 6), is_castling=True) in legal_moves
    assert Move((0, 4), (0, 2), is_castling=True) in legal_moves

    # Castle, confirm the rook and king are on the right squares, and then undo that castle.
    board.make_move(Move((0, 4), (0, 6), is_castling=True))
    assert board.squares[0][6] == "k" and board.squares [0][5] == "r"
    board.undo_move()
    assert board.squares[0][6] == "." and board.squares [0][5] == "."
    assert board.squares[0][4] == "k" and board.squares [0][7] == "r"
    assert board.castling_rights == "KQkq"

    # Assert that black can't castle if a piece is in the castling path
    board.squares[0][5] = "b"
    legal_moves = board.generate_legal_moves()
    assert Move((0, 4), (0, 6), is_castling=True) not in legal_moves

def test_en_passant1():
    board = Board()
    # Creating empty board
    board.load_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    en_passant = Move((3, 4), (2, 3), is_en_passant=True)
    legal_moves = board.generate_legal_moves()

    # Confirm en passant is a candidate move
    assert en_passant in legal_moves

    # Check d6, d5, and e5 after en passant move has been made
    board.make_move(en_passant)
    assert board.squares[2][3] == "P"
    assert board.squares[3][3] == "."
    assert board.squares[3][4] == "."

    board.undo_move()
    assert board.squares[2][3] == "."
    assert board.squares[3][3] == "p"
    assert board.squares[3][4] == "P"
    assert board.en_passant_target == "d6"

def test_en_passant2():
    board = Board()
    board.load_fen("4k3/8/8/8/3pP3/8/8/4K3 b - e3 0 1")
    en_passant = Move((4, 3), (5, 4), is_en_passant=True)

    # Confirm en passant is a candidate move
    assert en_passant in board.generate_legal_moves()

    # Check squares affected by en passant after move is made
    board.make_move(en_passant)
    assert board.squares[5][4] == "p"
    assert board.squares[4][4] == "."
    assert board.squares[4][3] == "."

    board.undo_move()
    assert board.squares[5][4] == "."
    assert board.squares[4][4] == "P"
    assert board.squares[4][3] == "p"
    assert board.en_passant_target == "e3"

def test_en_passant3():
    board = Board()
    board.load_fen("4k3/8/8/3pP3/8/8/8/4K3 w - - 0 1")
    en_passant = Move((3, 4), (2, 3), is_en_passant=True)

    assert en_passant not in board.generate_legal_moves()

def test_en_passant4():
    board = Board()
    board.load_fen("4k3/8/8/r2pP2K/8/8/8/8 w - d6 0 1")
    en_passant = Move((3, 4), (2, 3), is_en_passant=True)

    assert en_passant in board.generate_pseudo_legal_moves()
    assert en_passant not in board.generate_legal_moves()
