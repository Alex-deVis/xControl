class Offset:
    """Distance between two points on screen."""

    def __init__(self, X: int, Y: int) -> None:
        assert isinstance(X, int) and isinstance(Y, int)
        self.X = X
        self.Y = Y

    def __repr__(self) -> str:
        return f"Offset({self.X}, {self.Y})"


class Point:
    """Point on screen. (0, 0) is top left corner."""

    def __init__(self, X: int, Y: int) -> None:
        assert isinstance(X, int) and isinstance(Y, int) and X >= 0 and Y >= 0
        self.X = X
        self.Y = Y

    def __add__(self, offset: Offset) -> "Point":
        assert isinstance(offset, Offset)
        return Point(self.X + offset.X, self.Y + offset.Y)

    def __eq__(self, other: "Point") -> bool:
        assert isinstance(other, Point)
        return self.X == other.X and self.Y == other.Y

    def __repr__(self) -> str:
        return f"Point({self.X}, {self.Y})"


class Frame:
    """Rectangle on screen defined by top left corner, width and height."""

    def __init__(self, corner: Point, width: int, height: int) -> None:
        assert (
            isinstance(corner, Point)
            and isinstance(width, int)
            and isinstance(height, int)
        )
        self.corner = corner
        self.width = width
        self.height = height

    def get_top_left(self) -> Point:
        return self.corner

    def get_center(self) -> Point:
        return self.corner + Offset(self.width // 2, self.height // 2)

    def get_bottom_right(self) -> Point:
        return self.corner + Offset(self.width, self.height)

    def __repr__(self) -> str:
        return f"Frame({self.corner}, {self.width}, {self.height})"


class RelativeFrame:
    """Relative rectangle on screen defined by offset from reference point, width and height."""

    def __init__(self, offset: Offset, width: int, height: int) -> None:
        assert (
            isinstance(offset, Offset)
            and isinstance(width, int)
            and isinstance(height, int)
        )
        self.offset = offset
        self.width = width
        self.height = height

    def to_frame(self, reference: Point) -> Frame:
        return Frame(reference + self.offset, self.width, self.height)

    def __repr__(self) -> str:
        return f"RelativeFrame({self.offset}, {self.width}, {self.height})"
