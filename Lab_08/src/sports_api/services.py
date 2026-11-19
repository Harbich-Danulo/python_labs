"""Сервісний шар (Business Logic Layer) для обліку спортивних результатів та аналітики."""

from typing import Any, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sports_api.models import Athlete, Result, Sport
from sports_api.repositories import AthleteRepository, ResultRepository, SportRepository
from sports_api.schemas import (
    RankedAthleteItem,
    SportRankingResponse,
    SportStatisticsResponse,
)


class EntityNotFoundError(Exception):
    """Помилка: сутність не знайдена у базі даних."""
    pass


class BusinessValidationError(Exception):
    """Помилка порушення бізнес-правил або валідації."""
    pass


class ConflictError(Exception):
    """Конфлікт даних (наприклад, дублікат унікального імені)."""
    pass


class SportsService:
    """Сервіс координації бізнес-логіки та аналітичних розрахунків."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.sports_repo = SportRepository(session)
        self.athletes_repo = AthleteRepository(session)
        self.results_repo = ResultRepository(session)

    # --- Методи видів спорту ---

    def register_sport(self, name: str, unit: str, is_lower_better: bool = False) -> Sport:
        clean_name = name.strip()
        if not clean_name:
            raise BusinessValidationError("Назва виду спорту не може бути порожньою.")
        existing = self.sports_repo.get_by_name(clean_name)
        if existing:
            raise ConflictError(f"Вид спорту '{clean_name}' вже зареєстровано.")
        return self.sports_repo.create(clean_name, unit.strip(), is_lower_better)

    def get_sport(self, sport_id: int) -> Sport:
        sport = self.sports_repo.get_by_id(sport_id)
        if not sport:
            raise EntityNotFoundError(f"Вид спорту ID {sport_id} не знайдено.")
        return sport

    def list_sports(self) -> List[Sport]:
        return self.sports_repo.list_all()

    # --- Методи спортсменів ---

    def register_athlete(self, name: str, country: str = "Україна", age: int = 20) -> Athlete:
        clean_name = name.strip()
        if not clean_name:
            raise BusinessValidationError("Ім'я спортсмена не може бути порожнім.")
        if age < 5 or age > 120:
            raise BusinessValidationError(f"Неприпустимий вік спортсмена: {age}.")
        return self.athletes_repo.create(clean_name, country.strip(), age)

    def get_athlete(self, athlete_id: int) -> Athlete:
        athlete = self.athletes_repo.get_by_id(athlete_id)
        if not athlete:
            raise EntityNotFoundError(f"Спортсмена ID {athlete_id} не знайдено.")
        return athlete

    def list_athletes(
        self, name_query: Optional[str] = None, country: Optional[str] = None
    ) -> List[Athlete]:
        return self.athletes_repo.list_all(name_query=name_query, country=country)

    def update_athlete(self, athlete_id: int, **fields: Any) -> Athlete:
        athlete = self.get_athlete(athlete_id)
        if "age" in fields and fields["age"] is not None:
            age = fields["age"]
            if age < 5 or age > 120:
                raise BusinessValidationError(f"Неприпустимий вік спортсмена: {age}.")
        if "name" in fields and fields["name"] is not None:
            fields["name"] = fields["name"].strip()
            if not fields["name"]:
                raise BusinessValidationError("Ім'я спортсмена не може бути порожнім.")
        return self.athletes_repo.update(athlete, **fields)

    def delete_athlete(self, athlete_id: int) -> None:
        athlete = self.get_athlete(athlete_id)
        self.athletes_repo.delete(athlete)

    # --- Методи результатів ---

    def record_result(
        self,
        athlete_id: int,
        sport_id: int,
        score: float,
        category: str,
        competition_name: Optional[str] = None,
    ) -> Result:
        if score <= 0:
            raise BusinessValidationError(f"Результат повинен бути більше нуля, отримано: {score}.")
        # Перевірка існування спортсмена та спорту
        self.get_athlete(athlete_id)
        self.get_sport(sport_id)

        return self.results_repo.create(
            athlete_id=athlete_id,
            sport_id=sport_id,
            score=score,
            category=category.strip(),
            competition_name=competition_name.strip() if competition_name else None,
        )

    def get_result(self, result_id: int) -> Result:
        result = self.results_repo.get_by_id(result_id)
        if not result:
            raise EntityNotFoundError(f"Результат ID {result_id} не знайдено.")
        return result

    def update_result(self, result_id: int, **fields: Any) -> Result:
        result = self.get_result(result_id)
        if "score" in fields and fields["score"] is not None:
            if fields["score"] <= 0:
                raise BusinessValidationError(f"Результат повинен бути більше нуля: {fields['score']}.")
        return self.results_repo.update(result, **fields)

    def delete_result(self, result_id: int) -> None:
        result = self.get_result(result_id)
        self.results_repo.delete(result)

    def get_sport_results(
        self,
        sport_id: int,
        category: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
    ) -> List[Result]:
        self.get_sport(sport_id)
        return self.results_repo.filter_by_sport(sport_id, category, min_score, max_score)

    # --- Аналітика та формування рейтингу ---

    def get_sport_ranking(self, sport_id: int) -> SportRankingResponse:
        sport = self.get_sport(sport_id)

        stmt = select(Result).where(Result.sport_id == sport_id).join(Result.athlete)
        if sport.is_lower_better:
            stmt = stmt.order_by(Result.score.asc())
        else:
            stmt = stmt.order_by(Result.score.desc())

        results = self.session.execute(stmt).scalars().all()
        total_results = len(results)

        ranking_items: List[RankedAthleteItem] = []
        scores: List[float] = []

        for idx, res in enumerate(results, start=1):
            scores.append(res.score)
            ranking_items.append(
                RankedAthleteItem(
                    rank=idx,
                    athlete_id=res.athlete_id,
                    athlete_name=res.athlete.name,
                    country=res.athlete.country,
                    score=res.score,
                    category=res.category,
                    competition=res.competition_name or "—",
                )
            )

        best_score = scores[0] if scores else None
        avg_score = round(sum(scores) / total_results, 2) if total_results > 0 else 0.0

        return SportRankingResponse(
            sport_id=sport.id,
            sport_name=sport.name,
            unit=sport.unit,
            is_lower_better=sport.is_lower_better,
            total_results=total_results,
            best_score=best_score,
            average_score=avg_score,
            ranking=ranking_items,
        )

    def get_sport_statistics(self, sport_id: int) -> SportStatisticsResponse:
        sport = self.get_sport(sport_id)

        stmt = select(
            func.count(Result.id),
            func.avg(Result.score),
            func.min(Result.score),
            func.max(Result.score),
        ).where(Result.sport_id == sport_id)

        row = self.session.execute(stmt).one()
        count_val: Any = row[0]
        avg_val: Any = row[1]
        min_val: Any = row[2]
        max_val: Any = row[3]

        return SportStatisticsResponse(
            sport_id=sport.id,
            sport_name=sport.name,
            unit=sport.unit,
            total_results=int(count_val) if count_val is not None else 0,
            avg_score=round(float(avg_val), 2) if avg_val is not None else 0.0,
            min_score=float(min_val) if min_val is not None else 0.0,
            max_score=float(max_val) if max_val is not None else 0.0,
        )
