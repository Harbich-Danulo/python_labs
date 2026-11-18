"""Реалізація патерну Repository для збереження та доступу до сутностей бази даних."""

from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sports_db.models import Athlete, Result, Sport


class SportRepository:
    """Репозиторій для роботи з сутністю Sport."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, unit: str, is_lower_better: bool = False) -> Sport:
        sport = Sport(name=name, unit=unit, is_lower_better=is_lower_better)
        self.session.add(sport)
        self.session.flush()
        return sport

    def get_by_id(self, sport_id: int) -> Optional[Sport]:
        stmt = select(Sport).where(Sport.id == sport_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Sport]:
        stmt = select(Sport).where(Sport.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[Sport]:
        stmt = select(Sport).order_by(Sport.name)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, sport_id: int, **fields: Any) -> Optional[Sport]:
        sport = self.get_by_id(sport_id)
        if not sport:
            return None
        for key, value in fields.items():
            if hasattr(sport, key):
                setattr(sport, key, value)
        self.session.flush()
        return sport

    def delete(self, sport_id: int) -> bool:
        sport = self.get_by_id(sport_id)
        if not sport:
            return False
        self.session.delete(sport)
        self.session.flush()
        return True


class AthleteRepository:
    """Репозиторій для роботи з сутністю Athlete."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, country: str = "Україна", age: int = 20) -> Athlete:
        athlete = Athlete(name=name, country=country, age=age)
        self.session.add(athlete)
        self.session.flush()
        return athlete

    def get_by_id(self, athlete_id: int) -> Optional[Athlete]:
        stmt = select(Athlete).where(Athlete.id == athlete_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_name(self, name: str) -> List[Athlete]:
        stmt = select(Athlete).where(Athlete.name == name)
        return list(self.session.execute(stmt).scalars().all())

    def list_all(self) -> List[Athlete]:
        stmt = select(Athlete).order_by(Athlete.name)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, athlete_id: int, **fields: Any) -> Optional[Athlete]:
        athlete = self.get_by_id(athlete_id)
        if not athlete:
            return None
        for key, value in fields.items():
            if hasattr(athlete, key):
                setattr(athlete, key, value)
        self.session.flush()
        return athlete

    def delete(self, athlete_id: int) -> bool:
        athlete = self.get_by_id(athlete_id)
        if not athlete:
            return False
        self.session.delete(athlete)
        self.session.flush()
        return True


class ResultRepository:
    """Репозиторій для роботи з сутністю Result."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        athlete_id: int,
        sport_id: int,
        score: float,
        category: str,
        competition_name: Optional[str] = None,
    ) -> Result:
        result = Result(
            athlete_id=athlete_id,
            sport_id=sport_id,
            score=score,
            category=category,
            competition_name=competition_name,
        )
        self.session.add(result)
        self.session.flush()
        return result

    def get_by_id(self, result_id: int) -> Optional[Result]:
        stmt = select(Result).where(Result.id == result_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[Result]:
        stmt = select(Result).order_by(Result.id)
        return list(self.session.execute(stmt).scalars().all())

    def filter_by_sport(self, sport_id: int) -> List[Result]:
        stmt = select(Result).where(Result.sport_id == sport_id).order_by(Result.score)
        return list(self.session.execute(stmt).scalars().all())

    def filter_by_athlete(self, athlete_id: int) -> List[Result]:
        stmt = select(Result).where(Result.athlete_id == athlete_id).order_by(Result.created_at)
        return list(self.session.execute(stmt).scalars().all())

    def filter_by_category(self, category: str) -> List[Result]:
        stmt = select(Result).where(Result.category == category).order_by(Result.score)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, result_id: int, **fields: Any) -> Optional[Result]:
        result = self.get_by_id(result_id)
        if not result:
            return None
        for key, value in fields.items():
            if hasattr(result, key):
                setattr(result, key, value)
        self.session.flush()
        return result

    def delete(self, result_id: int) -> bool:
        result = self.get_by_id(result_id)
        if not result:
            return False
        self.session.delete(result)
        self.session.flush()
        return True
