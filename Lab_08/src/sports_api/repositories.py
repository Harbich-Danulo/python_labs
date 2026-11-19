"""Репозиторії збереження даних (Persistence Layer) для доступу до сутностей SQLite."""

from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sports_api.models import Athlete, Result, Sport


class SportRepository:
    """Репозиторій для роботи з сутністю Sport."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, unit: str, is_lower_better: bool = False) -> Sport:
        sport = Sport(name=name, unit=unit, is_lower_better=is_lower_better)
        self.session.add(sport)
        self.session.commit()
        self.session.refresh(sport)
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

    def update(self, sport: Sport, **fields: Any) -> Sport:
        for key, value in fields.items():
            if value is not None and hasattr(sport, key):
                setattr(sport, key, value)
        self.session.commit()
        self.session.refresh(sport)
        return sport

    def delete(self, sport: Sport) -> None:
        self.session.delete(sport)
        self.session.commit()


class AthleteRepository:
    """Репозиторій для роботи з сутністю Athlete."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, name: str, country: str = "Україна", age: int = 20) -> Athlete:
        athlete = Athlete(name=name, country=country, age=age)
        self.session.add(athlete)
        self.session.commit()
        self.session.refresh(athlete)
        return athlete

    def get_by_id(self, athlete_id: int) -> Optional[Athlete]:
        stmt = select(Athlete).where(Athlete.id == athlete_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(
        self, name_query: Optional[str] = None, country: Optional[str] = None
    ) -> List[Athlete]:
        stmt = select(Athlete)
        if name_query:
            stmt = stmt.where(Athlete.name.ilike(f"%{name_query}%"))
        if country:
            stmt = stmt.where(Athlete.country.ilike(f"%{country}%"))
        stmt = stmt.order_by(Athlete.name)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, athlete: Athlete, **fields: Any) -> Athlete:
        for key, value in fields.items():
            if value is not None and hasattr(athlete, key):
                setattr(athlete, key, value)
        self.session.commit()
        self.session.refresh(athlete)
        return athlete

    def delete(self, athlete: Athlete) -> None:
        self.session.delete(athlete)
        self.session.commit()


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
        self.session.commit()
        self.session.refresh(result)
        return result

    def get_by_id(self, result_id: int) -> Optional[Result]:
        stmt = select(Result).where(Result.id == result_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[Result]:
        stmt = select(Result).order_by(Result.id.desc())
        return list(self.session.execute(stmt).scalars().all())

    def filter_by_sport(
        self,
        sport_id: int,
        category: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
    ) -> List[Result]:
        stmt = select(Result).where(Result.sport_id == sport_id)
        if category:
            stmt = stmt.where(Result.category.ilike(f"%{category}%"))
        if min_score is not None:
            stmt = stmt.where(Result.score >= min_score)
        if max_score is not None:
            stmt = stmt.where(Result.score <= max_score)
        stmt = stmt.order_by(Result.score)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, result: Result, **fields: Any) -> Result:
        for key, value in fields.items():
            if value is not None and hasattr(result, key):
                setattr(result, key, value)
        self.session.commit()
        self.session.refresh(result)
        return result

    def delete(self, result: Result) -> None:
        self.session.delete(result)
        self.session.commit()
