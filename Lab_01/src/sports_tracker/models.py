"""Data models for sports results tracking."""

from dataclasses import dataclass


class InvalidAthleteDataError(ValueError):
    """Raised when athlete data fails validation."""
    pass


@dataclass(frozen=False)
class Athlete:
    """Represents an athlete and their performance result.

    Attributes:
        name: Full name of the athlete.
        sport: Discipline or type of sport.
        result: Numeric measurement of the result (e.g. points, seconds, meters).
        category: Competition category (e.g. 'Juniors', 'Seniors', 'U-21', 'Masters').
    """

    name: str
    sport: str
    result: float
    category: str

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self.name = self.name.strip()
        self.sport = self.sport.strip()
        self.category = self.category.strip()

        if not self.name:
            raise InvalidAthleteDataError("Athlete name cannot be empty.")
        if not self.sport:
            raise InvalidAthleteDataError("Sport name cannot be empty.")
        if not self.category:
            raise InvalidAthleteDataError("Category cannot be empty.")
        if self.result < 0:
            raise InvalidAthleteDataError(
                f"Result cannot be negative. Received: {self.result}"
            )

    @property
    def display_info(self) -> str:
        """Return formatted one-line representation."""
        return f"{self.name} | {self.sport} | {self.result:.2f} | {self.category}"
