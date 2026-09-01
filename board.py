from move import Move

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

class Board:
    def __init__(self):
        self.squares = starting_position()
        self.side_to_move = "w"
        self.castling_rights = "KQkq"
        self.en_passant_target = "-"
        self.halfmove = 0
        self.fullmove = 1

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

if __name__ == '__main__':
   pass
