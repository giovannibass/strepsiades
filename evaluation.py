# Print the material score of each side
def evaluate(board):
    all_squares = []
    all_pieces = []
    white_pieces = []
    black_pieces = []
    values = {
    "P": 100,
    "N": 300,
    "B": 300,
    "R": 500,
    "Q": 900,
    }


   # Get all the squares on the board
    for square in board.squares:
        all_squares.extend(square)
    
    # Remove the empty squares
    for piece in all_squares:
        if piece != ".":
            all_pieces.append(piece)

    # Create one list containing white pieces and the other list containing black pieces
    for piece in all_pieces:
        if piece.isupper():
            white_pieces.append(piece)
        else:
            black_pieces.append(piece)
    
    white_total = 0
    black_total = 0
    for piece in white_pieces:
        if piece.upper() == "K":
            continue
        white_total += values[piece.upper()]

    for piece in black_pieces:
        if piece.upper() == "K":
            continue
        black_total += values[piece.upper()]

    return white_total - black_total

if __name__ == "__main__":
    pass
