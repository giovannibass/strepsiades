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

    def display(self):
        rank = 8
        for x in self.squares:
            piece = " ".join(x)
            print(f"{rank}  {piece}")
            rank -= 1
        print("   a b c d e f g h")
            

if __name__ == '__main__':
    board = Board()

    valid_fen = "8/8/8/8/8/8/8/K6k w - - 0 1"
    invalid_fen = "8/8/8/8/8/8/8/Q6q x - - 12 30"

    board.load_fen(valid_fen)

    print("Before invalid attempt:")
    print(board.__dict__)

    try:
        board.load_fen(invalid_fen)
    except ValueError as error:
        print("Rejected:", error)

    print("After invalid attempt:")
    print(board.__dict__) 
