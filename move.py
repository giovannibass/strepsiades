# Represents a move. Tells us where a piece starts, finishes, or if a special move is being done.

from dataclasses import dataclass

@dataclass(frozen=True)
class Move:
    start: tuple[int, int]
    end: tuple[int, int]
    promotion: str | None = None
    is_castling: bool = False
    is_en_passant: bool = False

if __name__ == "__main__":
    normal_move = Move((6, 4), (4, 4))
    identical_normal_move = Move((6, 4), (4, 4))
    queen_move = Move((1, 0), (0, 0), "q")
    knight_move = Move((1, 0), (0, 0), "n")
    print(normal_move)
    print(normal_move == identical_normal_move)
    print(queen_move == knight_move)
