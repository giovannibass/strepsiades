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
    pass
