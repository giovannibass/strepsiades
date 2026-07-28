import argparse
from board import Board

def main():
    parser = argparse.ArgumentParser(
            description="Takes a FEN string as input and returns a display of that current chess position"
    )

    # Add --fen option
    parser.add_argument(
            "--fen",
            required=True,
            help="The entire FEN string that will be represented"
    )

    # Creating object for NameSpace class. arguments.fen attribute is created here
    arguments = parser.parse_args()
    
    board = Board()

    # Error handling for when ValueErrors are raised
    try:
        board.load_fen(arguments.fen)
    except ValueError as error:
        parser.error(str(error))

    board.display()

if __name__ == "__main__":
    main()
