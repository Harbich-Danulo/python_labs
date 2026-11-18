"""Сервісний шар (Business Logic / Service Layer) для обліку спортивних результатів.

Забезпечує координацію репозиторіїв, обчислення аналітичних показників
(найкращий результат, середній бал, рейтинг) та транзакційні операції з підтримкою ACID.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sports_db.models import Athlete, Result, Sport
from sports_db.repositories import AthleteRepository, ResultRepository, SportRepository


class ValidationError(Exception):
    """Помилка валідації бізнес-правил."""
    pass


class SportsService:
    """Сервіс координації бізнес-логіки та транзакцій."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.sports_repo = SportRepository(session)
        self.athletes_repo = AthleteRepository(session)
        self.results_repo = ResultRepository(session)

    def register_sport(self, name: str, unit: str, is_lower_better: bool = False) -> Sport:
        """Реєструє новий вид спорту з валідацією назви."""
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValidationError("Назва виду спорту не може бути порожньою.")
        existing = self.sports_repo.get_by_name(cleaned_name)
        if existing:
            raise ValidationError(f"Вид спорту '{cleaned_name}' вже зареєстровано.")
        sport = self.sports_repo.create(cleaned_name, unit.strip(), is_lower_better)
        self.session.commit()
        return sport

    def register_athlete(self, name: str, country: str = "Україна", age: int = 20) -> Athlete:
        """Реєструє нового спортсмена з перевіркою віку."""
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValidationError("Ім'я спортсмена не може бути порожнім.")
        if age < 5 or age > 120:
            raise ValidationError(f"Некоректний вік спортсмена: {age}.")
        athlete = self.athletes_repo.create(cleaned_name, country.strip(), age)
        self.session.commit()
        return athlete

    def record_result(
        self,
        athlete_id: int,
        sport_id: int,
        score: float,
        category: str,
        competition_name: Optional[str] = None,
    ) -> Result:
        """Реєструє спортивний результат з валідацією зовнішніх ключів та балів."""
        if score < 0:
            raise ValidationError(f"Результат не може бути від'ємним: {score}.")
        athlete = self.athletes_repo.get_by_id(athlete_id)
        if not athlete:
            raise ValidationError(f"Спортсмена з ID {athlete_id} не знайдено.")
        sport = self.sports_repo.get_by_id(sport_id)
        if not sport:
            raise ValidationError(f"Вид спорту з ID {sport_id} не знайдено.")

        res = self.results_repo.create(
            athlete_id=athlete_id,
            sport_id=sport_id,
            score=score,
            category=category.strip(),
            competition_name=competition_name.strip() if competition_name else None,
        )
        self.session.commit()
        return res

    def get_best_result(self, sport_id: int) -> Optional[Result]:
        """Знаходить найкращий результат з урахуванням специфіки дисципліни (менше/більше значення)."""
        sport = self.sports_repo.get_by_id(sport_id)
        if not sport:
            raise ValidationError(f"Вид спорту з ID {sport_id} не знайдено.")

        stmt = select(Result).where(Result.sport_id == sport_id)
        if sport.is_lower_better:
            stmt = stmt.order_by(Result.score.asc())
        else:
            stmt = stmt.order_by(Result.score.desc())

        return self.session.execute(stmt).scalars().first()

    def get_average_score(self, sport_id: int) -> float:
        """Обчислює середній результат за видом спорту за допомогою SQL AVG()."""
        sport = self.sports_repo.get_by_id(sport_id)
        if not sport:
            raise ValidationError(f"Вид спорту з ID {sport_id} не знайдено.")

        stmt = select(func.avg(Result.score)).where(Result.sport_id == sport_id)
        avg_val = self.session.execute(stmt).scalar()
        return round(float(avg_val), 2) if avg_val is not None else 0.0

    def build_ranking(self, sport_id: int) -> List[Dict[str, Any]]:
        """Формує відсортований рейтинг спортсменів для зазначеної дисципліни."""
        sport = self.sports_repo.get_by_id(sport_id)
        if not sport:
            raise ValidationError(f"Вид спорту з ID {sport_id} не знайдено.")

        stmt = (
            select(Result)
            .where(Result.sport_id == sport_id)
            .join(Result.athlete)
        )
        if sport.is_lower_better:
            stmt = stmt.order_by(Result.score.asc())
        else:
            stmt = stmt.order_by(Result.score.desc())

        results = self.session.execute(stmt).scalars().all()
        ranking: List[Dict[str, Any]] = []
        for rank, res in enumerate(results, start=1):
            ranking.append({
                "rank": rank,
                "athlete_name": res.athlete.name,
                "country": res.athlete.country,
                "score": res.score,
                "unit": sport.unit,
                "category": res.category,
                "competition": res.competition_name or "—",
            })
        return ranking

    def bulk_register_results_transactional(
        self, items: List[Dict[str, Any]]
    ) -> List[Result]:
        """Транзакційне пакетне додавання результатів із демонстрацією принципу Atomicity (ACID).
        
        Якщо бодай один запис некоректний (наприклад, score < 0 або неіснуючий athlete_id),
        викликається session.rollback(), і жоден результат не потрапляє в базу даних.
        """
        created_records: List[Result] = []
        try:
            for item in items:
                athlete_id = int(item["athlete_id"])
                sport_id = int(item["sport_id"])
                score = float(item["score"])
                category = str(item["category"])
                competition = item.get("competition_name")

                if score < 0:
                    raise ValidationError(
                        f"Неприпустимий від'ємний результат: {score} для athlete_id={athlete_id}"
                    )
                athlete = self.athletes_repo.get_by_id(athlete_id)
                if not athlete:
                    raise ValidationError(f"Спортсмена ID {athlete_id} не знайдено.")
                sport = self.sports_repo.get_by_id(sport_id)
                if not sport:
                    raise ValidationError(f"Вид спорту ID {sport_id} не знайдено.")

                res = self.results_repo.create(
                    athlete_id=athlete_id,
                    sport_id=sport_id,
                    score=score,
                    category=category,
                    competition_name=competition,
                )
                created_records.append(res)

            # Фіксуємо всю транзакцію
            self.session.commit()
            return created_records
        except Exception:
            # При виникненні будь-якої помилки відкочуємо транзакцію повністю
            self.session.rollback()
            raise
