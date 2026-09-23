from move import Move
from dataclasses import dataclass

# Matrix for the chessboard

def starting_position():
    return [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]

# Validate and expand one rank
def parse_rank(rank_text):
    row = []
    valid_symbols = ("p", "n", "b", "r", "q", "k", "P", "N", "B", "R", "Q", "K")

    # Keeps track if the previous character was a digit
    previous_is_digit = False

    for char in rank_text:
        # If character is a valid digit, add the appropiate number of empty spaces.
        if char.isdigit():
            if char not in "12345678":
                raise ValueError("Invalid digit in FEN rank")

            # If previous character is digit raise error.
            if previous_is_digit:
                raise ValueError("Consecutive digits detected in FEN rank")

            previous_is_digit = True
            row.extend("." * int(char))

        # Confirm that the character is a valid piece symbol. If so add it to the list.
        elif char in valid_symbols:
            previous_is_digit = False
            row.append(char)
        else:
            raise ValueError("Invalid piece detected")

    return row

# Splits the piece placement of FEN into each rank and runs it through parse_rank().
def parse_piece_placement(piece_place):
    board = []

    # Split into ranks
    ranks = piece_place.split("/")

    # Make sure that there are 8 ranks.
    if len(ranks) != 8:
        raise ValueError("FEN piece placement must have 8 ranks")

    for rank in ranks:

        # Make sure each rank contains 8 squares
        row = parse_rank(rank)
        if len(row) != 8:
            raise ValueError("Each rank must contain 8 squares")

        # Add the parsed rank to board
        board.append(row)

    return board

def validate_castle(castling):

    # Validation for castling rights
    allowed = ("K", "Q", "k", "q", "-")

    for char in castling:
        # Only valid symbols are allowed
        if char not in allowed:
            raise ValueError("Invalid castling rights")

    # If '-' is used there should be no other symbols
    if '-' in castling and len(castling) != 1:
        raise ValueError("Null castling rights (-) should not be mixed with other symbols")

    # No duplicate entries
    elif len(castling) != len(set(castling)):
        raise ValueError("Duplicate entry in castling rights")

def validate_en_passant(en_passant):

    if en_passant == '-':
        return

    # If '-' is used there should be no other symbols
    if '-' in en_passant and len(en_passant) != 1:
        raise ValueError("No target square (-) should not be mixed with other symbols")

    # En passant target square should only be 2 characters
    if len(en_passant) != 2:
        raise ValueError("En passant target square should be 2 characters")

    file = en_passant[0]
    rank = en_passant[1]

    # Needs a valid file
    if file not in ("a", "b", "c", "d", "e", "f", "g", "h"):
        raise ValueError("Invalid file for en passant target square")

    # Target squares can only be on the third or sixth rank
    elif rank not in ("3", "6"):
        raise ValueError("Invalid rank for en passant target square")

def validate_half_full(half, full):

    half = int(half)
    full = int(full)

    if half < 0:
        raise ValueError("Halfmove counter needs to be greater than or equal to 0")

    if full < 1:
        raise ValueError("Fullmove counter needs to be greater tan or equal to 1")

    return half, full

@dataclass(frozen=True)
class _UndoRecord:
    move: Move
    changed_squares: tuple[tuple[int, int, str], ...]
    side_to_move: str
    castling_rights: str
    en_passant_target: str
    halfmove: int
    fullmove: int

class Board:
    def __init__(self):
        # Default FEN components
        self.squares = starting_position()
        self.side_to_move = "w"
        self.castling_rights = "KQkq"
        self.en_passant_target = "-"
        self.halfmove = 0
        self.fullmove = 1

        # History for undoing moves
        self._history: list[_UndoRecord] = []

    def get_piece(self, row, col):
        return self.squares[row][col]

    # Validates the full FEN.
    def load_fen(self, full_fen):
        fen = full_fen.split()

        # Each full FEN has 6 fields
        if len(fen) != 6:
            raise ValueError("FEN requires 6 fields")

        # Checking that active color is 'w' or 'b'
        active_color = fen[1]
        if active_color not in ('w', 'b'):
            raise ValueError("Active color must be white (w) or black (b)")


        # Castling rights validation
        castle_input = fen[2]
        validate_castle(castle_input)

        # En passant validation
        en_passant = fen[3]
        validate_en_passant(en_passant)

        # Half-move and full move counter validation
        halfmove_clock, fullmove_number = validate_half_full(fen[4], fen[5])


        # Assiging parsed pieces to the board
        self.squares = parse_piece_placement(fen[0])
        self.side_to_move = active_color
        self.castling_rights = castle_input
        self.en_passant_target = en_passant
        self.halfmove = halfmove_clock
        self.fullmove = fullmove_number

    # Terminal display for the chessboard
    def display(self):
        rank = 8
        for x in self.squares:
            piece = " ".join(x)
            print(f"{rank}  {piece}")
            rank -= 1
        print("   a b c d e f g h")

    # Determines if a coordinate actually exists on the board.
    def is_in_bounds(self, row, column):
        return 0 <= row <= 7 and 0 <= column <= 7

    # Checks to see if a square is empty
    def is_empty(self, row, column):
        return self.is_in_bounds(row, column) and self.squares[row][column] == "."

    # Checks to see what color a piece is
    def piece_color(self, row, column):
        if not self.is_in_bounds(row, column) or self.is_empty(row, column):
            return None
        if self.squares[row][column].isupper():
            return "w"
        else:
            return "b"

    # Checks if a friendly piece is at a square
    def is_friendly_piece(self, row, column, color):
        # Returns True if the square has a piece of the same color
        return self.piece_color(row, column) == color

    # Checks if an enemy piece is at a square
    def is_enemy_piece(self, row, column, color):
        piece_color = self.piece_color(row, column)
        # Returns True if square is in bounds, not empty, and is not a friendly piece
        return piece_color is not None and piece_color != color

    # Generates pseudo-legal knight moves
    def generate_knight_moves(self, row, column):

        # All the ways a knight can move
        knight_offsets = [
                (1, 2),
                (2, 1),
                (-1, -2),
                (-2, -1),
                (-1, 2),
                (-2, 1),
                (1, -2),
                (2, -1)
        ]

        # Specifying the color to be used
        color = self.piece_color(row, column)

        # Guard clauses to make sure there's a knight on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        elif self.get_piece(row, column) not in ('n', 'N'):
            raise ValueError("Specified square does not have a knight")

        # Empty list that will store accepted coordinates as Move objects.
        moves = []

        for row_offset, column_offset in knight_offsets:
            destination_row = row + row_offset
            destination_column = column + column_offset

            # Check that destination coordinate is in bounds and not friendly
            if self.is_in_bounds(destination_row, destination_column) and not self.is_friendly_piece(destination_row, destination_column, color):

                # Create move objects and add them to moves list.
                moves.append(Move((row, column), (destination_row, destination_column)))

        return moves

    # Generates pseudo-legal sliding moves used by rook, bishop, and queen
    def generate_sliding_moves(self, row, column, directions):

        # Guard clauses to make sure there's a piece on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        if self.is_empty(row, column):
            raise ValueError("Square cannot be empty")

        # Specify the color that's being used
        color = self.piece_color(row, column)


        # Stores the results of the sliding moves
        moves = []

        for row_offset, column_offset in directions:

            # Apply offset to first destination
            destination_row = row + row_offset
            destination_column = column  + column_offset

            while self.is_in_bounds(destination_row, destination_column):

                # If piece is friendly then stop the while loop
                if self.is_friendly_piece(destination_row, destination_column, color):
                    break

                # If square has an enemy piece, append capture and stop
                elif self.is_enemy_piece(destination_row, destination_column, color):
                    # Create move objects and add captures to the list.
                    moves.append(Move((row, column), (destination_row, destination_column)))
                    break

                else:
                    # Create move objects and add them to moves list.
                    moves.append(Move((row, column), (destination_row, destination_column)))

                    destination_row += row_offset
                    destination_column += column_offset

        return moves

    # Returns the rook moves created by the sliding move generator
    def generate_rook_moves(self, row, column):

        rook_directions = [
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ]

        # Guard clauses to make sure there's a rook on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        elif self.get_piece(row, column) not in ('r', 'R'):
            raise ValueError("Specified square does not have a rook")

        return self.generate_sliding_moves(row, column, rook_directions)

    # Returns the bishop moves created by the sliding move generator
    def generate_bishop_moves(self, row, column):

        bishop_directions = [
                (1, 1),
                (-1, 1),
                (1, - 1),
                (-1, -1)
            ]

        # Guard clauses to make sure there's a bishop on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        elif self.get_piece(row, column) not in ('b', 'B'):
            raise ValueError("Specified square does not have a bishop")

        return self.generate_sliding_moves(row, column, bishop_directions)


    # Returns the queen moves created by the sliding move generator
    def generate_queen_moves(self, row, column):

        queen_directions = [
                (1, 0),
                (0, 1),
                (-1, 0),
                (0, -1),
                (1, 1),
                (-1, 1),
                (1, - 1),
                (-1, -1)
            ]

        # Guard clauses to make sure there's a queen on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        elif self.get_piece(row, column) not in ('q', 'Q'):
            raise ValueError("Specified square does not have a queen")

        return self.generate_sliding_moves(row, column, queen_directions)

    # Generates pseudo-legal pawn moves
    def generate_pawn_moves(self, row, column):
        # Guard clauses to make sure there's a pawn on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        elif self.get_piece(row, column) not in ('p', 'P'):
            raise ValueError("Specified square does not have a pawn")

        # Confirming the color of the piece
        color = self.piece_color(row, column)

        # Defining movement pattern
        if color == 'w':
            direction = -1
            starting_row = 6
            promotion_row = 0
        else:
            direction = 1
            starting_row = 1
            promotion_row = 7

        # Creating list that will contain potential results
        destinations = []

        destination_row = row + direction
        destination_column = column

        # One-square check
        if self.is_empty(destination_row, destination_column):
            # Appending list with potential move.
            destinations.append((destination_row, destination_column))

            # Run validations for two-square push
            two_step_row = destination_row + direction

            if row == starting_row and self.is_empty(two_step_row, destination_column):
                destinations.append((two_step_row, destination_column))

        # Diagonal capture checks
        for column_offset in (-1, 1):
            # Variable to represent columns to the left and right
            diag_column = column + column_offset

            # Include enemy pieces found as potential moves
            if self.is_enemy_piece(destination_row, diag_column, color):
                destinations.append((destination_row, diag_column))

        # List for accepted moves that will include promotions
        moves = []

        # Adding promotions to moves
        for destination_row, destination_column in destinations:
            if destination_row == promotion_row:
                for promotion_piece in ("q", "r", "b", "n"):
                    moves.append(Move((row, column), (destination_row, destination_column), promotion_piece))
            else:
                moves.append(Move((row, column), (destination_row, destination_column)))

        return moves

    # Returns pseudo-legal king moves
    def generate_king_moves(self, row, column):
        king_offsets = [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1)
        ]

        # Guard clauses to make sure there's a king on a valid square.
        if not self.is_in_bounds(row, column):
            raise ValueError("Starting coordinate must be in bounds")
        elif self.get_piece(row, column) not in ('k', 'K'):
            raise ValueError("Specified square does not have a king")

        # Specifying the color to be used
        color = self.piece_color(row, column)

        # Empty list that will store accepted coordinates as Move objects.
        moves = []

        for row_offset, column_offset in king_offsets:
            destination_row = row + row_offset
            destination_column = column + column_offset

            # Check that destination coordinate is in bounds and not friendly
            if self.is_in_bounds(destination_row, destination_column) and not self.is_friendly_piece(destination_row, destination_column, color):

                # Create move objects and add them to moves list.
                moves.append(Move((row, column), (destination_row, destination_column)))

        return moves


    # Combines all pseudo-legal moves
    def generate_pseudo_legal_moves(self):
        moves = []

        # Loop through every square on the board.
        for row, board_row in enumerate(self.squares):
            for column, piece in enumerate(board_row):
                if self.piece_color(row, column) == self.side_to_move:

                    # Route each piece to their move generator
                    piece_type = piece.lower()

                    if piece_type == "p":
                        piece_moves = (self.generate_pawn_moves(row, column))
                    elif piece_type == "n":
                        piece_moves = (self.generate_knight_moves(row, column))
                    elif piece_type == "b":
                        piece_moves = (self.generate_bishop_moves(row, column))
                    elif piece_type == "r":
                        piece_moves = (self.generate_rook_moves(row, column))
                    elif piece_type == "q":
                        piece_moves = (self.generate_queen_moves(row, column))
                    elif piece_type == "k":
                        piece_moves = (self.generate_king_moves(row, column))

                    # Adding the stored moves to the flat `moves` list
                    moves.extend(piece_moves)

        return moves

    def make_move(self, move):
        # Making the undo record
        start_row, start_column = move.start
        end_row, end_column = move.end
        
        changed_squares = ((start_row, start_column, self.squares[start_row][start_column]), 
                           (end_row, end_column, self.squares[end_row][end_column]))
        
        # Replacing changed_squares when en passant is involved        
        if move.is_en_passant:
            changed_squares = (
                (start_row, start_column, self.squares[start_row][start_column]),
                (end_row, end_column, self.squares[end_row][end_column]),
                (start_row, end_column, self.squares[start_row][end_column])
            )
        
        # Replacing changed_squares when castling is involved
        if move.is_castling:
            if end_column == 6:
                rook_start_column = 7
                rook_end_column = 5
            elif end_column == 2:
                rook_start_column = 0
                rook_end_column = 3

            changed_squares = (
                (start_row, start_column, self.squares[start_row][start_column]),
                (end_row, end_column, self.squares[end_row][end_column]),
                (start_row, rook_start_column, self.squares[start_row][rook_start_column]),
                (start_row, rook_end_column, self.squares[start_row][rook_end_column])
            )

        record = _UndoRecord(
            move,
            changed_squares,
            self.side_to_move,
            self.castling_rights,
            self.en_passant_target,
            self.halfmove,
            self.fullmove
        )
        
        # Keeping record in self._history
        self._history.append(record)
        
        # Update halfmove counter when a pawn is moved or a capture is made
        # Capture is detected by seeing if the square a piece is moving to is occupied
        if self.get_piece(start_row, start_column) in ("P", "p") or not self.is_empty(end_row, end_column):
            self.halfmove = 0
        else:
            self.halfmove += 1

        # Update full-move counter
        if self.side_to_move == "b":
            self.fullmove += 1

        # Updating en passant target
        # Clearing the previous target square. Important in case the opponent decides to take en passant
        self.en_passant_target = "-"

        # See if a pawn moved and if it's a double pawn push
        if self.get_piece(start_row, start_column) in ("P", "p") and abs(end_row - start_row) == 2:
            # Calculate target row
            target_row = (start_row + end_row) // 2

            # Calculating target square
            self.en_passant_target = "abcdefgh"[start_column] + str(8 - target_row)

        # Updating castling rights
        moving_piece = self.get_piece(start_row, start_column)
        captured_piece = self.get_piece(end_row, end_column)

        king_rights = {
            "K": "KQ",
            "k": "kq"
        }

        rook_rights = {
            ("R", (7, 7)): "K",
            ("R", (7, 0)): "Q",
            ("r", (0, 7)): "k",
            ("r", (0, 0)): "q"
        }

        # Removing castling rights if king moves
        rights_to_remove = king_rights.get(moving_piece, "")
        
        # Removing castling rights if rook moves
        rights_to_remove += rook_rights.get((moving_piece, (start_row, start_column)), "")
        
        # Removing castling rights if rook is captured
        rights_to_remove += rook_rights.get((captured_piece, (end_row, end_column)), "")
        
        # Loop through castling rights
        for symbol in rights_to_remove:
            self.castling_rights = self.castling_rights.replace(symbol, "")
       
        # Clear castling rights if there are none left
        if self.castling_rights == "":
            self.castling_rights = "-"

        # Change side_to_move after the move has been made
        if self.side_to_move == "w":
            self.side_to_move = "b"
        else:
            self.side_to_move = "w"
        
        # Pawn promotion
        destination_piece = moving_piece

        if move.promotion is not None:
            if moving_piece.isupper():
                destination_piece = move.promotion.upper()
            else:
                destination_piece = move.promotion.lower()
        
        # Removing the pawn that was taken by enpassant.
        if move.is_en_passant:
            self.squares[start_row][end_column] = "."

        # Updating location of the rook after castling
        if move.is_castling:
            self.squares[start_row][rook_end_column] = self.squares[start_row][rook_start_column]
            self.squares[start_row][rook_start_column] = "."

        # Put moving piece on destination and empty the starting square
        self.squares[end_row][end_column] = destination_piece
        self.squares[start_row][start_column] = "."

    def undo_move(self):
        # Retrieve and remove the newest record
        record = self._history.pop()

        # Loop over changed_squares and restore each squre
        for row, column, previous_piece in record.changed_squares:
            self.squares[row][column] = previous_piece

        # Restoring other fields
        self.side_to_move = record.side_to_move
        self.castling_rights = record.castling_rights
        self.en_passant_target = record.en_passant_target
        self.halfmove = record.halfmove
        self.fullmove = record.fullmove

    def is_square_attacked(self, row, column, attacking_color):
        
        # All the ways a knight can move
        knight_offsets = [
            (1, 2),
            (2, 1),
            (-1, -2),
            (-2, -1),
            (-1, 2),
            (-2, 1),
            (1, -2),
            (2, -1)
        ]

        king_offsets = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1)
        ]

        orthogonal_ray = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]

        diagonal_ray = [
            (1, 1),
            (-1, 1),
            (1, - 1),
            (-1, -1)
        ]

        # Check if target is out of bounds
        if not self.is_in_bounds(row, column):
            raise ValueError("Target is out of bounds")

        if attacking_color not in ("w", "b"):
            raise ValueError("Color is not white or black")
        
        # Choose pawn symbol from attacking color
        if attacking_color == "w":
            source_row = row + 1
            pawn = "P"
            knight = "N"
            king = "K"
            orthogonal = ("R", "Q")
            diagonal = ("B", "Q")

        elif attacking_color == "b":
            source_row = row - 1
            pawn = "p"
            knight = "n"
            king = "k"
            orthogonal = ("r", "q")
            diagonal = ("b", "q")
        
        # Check if source squares have an attacking pawn
        for column_offset in (1, -1):
            source_column = column + column_offset
            
            # Make sure the attacking pawn is in bounds
            if not self.is_in_bounds(source_row, source_column):
                continue

            # Check each square to see if it has a pawn of the appropriate color
            if self.get_piece(source_row, source_column) == pawn:
                return True
        
        # Check if source squares have an attacking knight
        for row_offset, column_offset in knight_offsets:
            source_row = row + row_offset
            source_column = column + column_offset

            # Make sure the attacking knight is in bounds
            if not self.is_in_bounds(source_row, source_column):
                continue

            # Check each square to see if it has a knight of the appropriate color
            if self.get_piece(source_row, source_column) == knight:
                return True

        # Check if source squares have an attacking king
        for row_offset, column_offset in king_offsets:
            source_row = row + row_offset
            source_column = column + column_offset

            # Make sure the attacking king is in bounds
            if not self.is_in_bounds(source_row, source_column):
                continue

            # Check each square to see if it has a king of the appropriate color
            if self.get_piece(source_row, source_column) == king:
                return True

        # Figure out source row/column for orthogonal movements
        for row_offset, column_offset in orthogonal_ray:
            source_row = row + row_offset
            source_column = column + column_offset

            # See which squares are in orthogonal ray
            while self.is_in_bounds(source_row, source_column):
                # Check if a square has a piece on it
                if not self.is_empty(source_row, source_column):
                    # Check if that piece is a rook or queen
                    if self.get_piece(source_row, source_column) in orthogonal:
                        return True
                    else:
                        break
                
                # Add the offsets to provide the new square to check
                else:
                    source_row += row_offset
                    source_column += column_offset

        # Figure out source row/column for diagonal movements
        for row_offset, column_offset in diagonal_ray:
            source_row = row + row_offset
            source_column = column + column_offset

            # See which squares are in diagonal ray
            while self.is_in_bounds(source_row, source_column):
                # Check if a square has a piece on it
                if not self.is_empty(source_row, source_column):
                    # Check if that piece is a bishop or queen
                    if self.get_piece(source_row, source_column) in diagonal:
                        return True
                    else:
                        break
                
                # Add the offsets to provide the new square to check
                else:
                    source_row += row_offset
                    source_column += column_offset

        # Mark as False if no attackers are detected
        return False

    def is_in_check(self, color):
        if color == "w":
            king = "K"
            attacker = "b"
        elif color == "b":
            king = "k"
            attacker = "w"
        else:
            raise ValueError("Color must be 'w' or 'b'")

        # Loop through every square on the board and find the king
        for row, board_row in enumerate(self.squares):
            for column, piece in enumerate(board_row):
                if piece == king:
                    return self.is_square_attacked(row, column, attacker)

        raise ValueError("King is missing on board")
                

if __name__ == '__main__':
    pass
