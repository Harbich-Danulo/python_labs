"""TypedDict data transfer objects (DTO) for external payloads."""

from typing import NotRequired, TypedDict


class ScorePayload(TypedDict):
    """External payload format for score records."""
    value: float
    unit: str


class AthletePayload(TypedDict):
    """External payload format representing an athlete input."""
    id: int
    name: str
    country: str
    age: int


class ResultPayload(TypedDict):
    """External payload format for registering a sports competition result."""
    result_id: int
    athlete_id: int
    athlete_name: str
    country: str
    age: int
    sport_name: str
    competition_name: str
    location: str
    year: int
    score_value: float
    score_unit: str
    category: str
    notes: NotRequired[str]
