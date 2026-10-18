"""Application service layer with Dependency Injection (SOLID DIP)."""

from sports_app.dto import ResultPayload
from sports_app.models import (
    Athlete,
    AthleteCategory,
    Competition,
    HigherScoreWinsStrategy,
    LowerTimeWinsStrategy,
    RankingStrategy,
    RankingTable,
    Result,
    Sport,
)
from sports_app.protocols import Notifier, ResultExporter
from sports_app.repositories import InMemoryRepository
from sports_app.value_objects import PerformanceMetric, Score


class ConsoleNotifier:
    """Concrete notifier implementation (implements Notifier Protocol via structural typing)."""

    def send(self, recipient: str, message: str) -> None:
        print(f"[NOTIFICATION] To {recipient}: {message}")


class MarkdownExporter:
    """Concrete exporter implementation (implements ResultExporter Protocol)."""

    def export(self, title: str, content: str) -> str:
        formatted = f"# {title}\n\n{content}\n"
        print(f"[EXPORT] Generated Markdown report for '{title}'")
        return formatted


class SportsAccountingService:
    """Application Service orchestrating domain entities, repositories, and reporting with Dependency Injection."""

    def __init__(
        self,
        athlete_repo: InMemoryRepository[Athlete],
        result_repo: InMemoryRepository[Result],
        notifier: Notifier,
        exporter: ResultExporter,
    ) -> None:
        self._athlete_repo = athlete_repo
        self._result_repo = result_repo
        self._notifier = notifier
        self._exporter = exporter

    def register_result_from_payload(self, payload: ResultPayload) -> Result:
        """Register a new result using external TypedDict DTO."""
        athlete = Athlete(
            id=payload["athlete_id"],
            name=payload["athlete_name"],
            country=payload["country"],
            age=payload["age"],
        )
        self._athlete_repo.add(athlete)

        sport = Sport(
            id=payload["athlete_id"] * 10,
            name=payload["sport_name"],
            higher_is_better=payload["score_unit"] != "s",
            default_unit=payload["score_unit"],
        )

        competition = Competition(
            id=100,
            name=payload["competition_name"],
            location=payload["location"],
            year=payload["year"],
        )

        score = Score(value=payload["score_value"], unit=payload["score_unit"])

        result = Result(
            id=payload["result_id"],
            athlete=athlete,
            sport=sport,
            competition=competition,
            _score=score,
            category=AthleteCategory(payload["category"]),
        )
        self._result_repo.add(result)

        self._notifier.send(
            recipient="admin@olympic.ua",
            message=f"Зареєстровано новий результат: {athlete.name} — {score} ({sport.name})",
        )
        return result

    def find_by_sport(self, sport_name: str) -> list[Result]:
        """Find all results for a given sport discipline."""
        target = sport_name.strip().lower()
        return [r for r in self._result_repo.all() if r.sport.name.lower() == target]

    def find_best_result(self, sport_name: str) -> Result | None:
        """Find the best result in a sport considering whether higher or lower score wins."""
        results = self.find_by_sport(sport_name)
        if not results:
            return None
        higher_wins = results[0].sport.higher_is_better
        if higher_wins:
            return max(results, key=lambda r: r.score.value)
        return min(results, key=lambda r: r.score.value)

    def calculate_statistics(self, sport_name: str) -> PerformanceMetric | None:
        """Calculate statistical performance metric for a sport."""
        results = self.find_by_sport(sport_name)
        if not results:
            return None

        unit = results[0].score.unit
        total_val = sum(r.score.value for r in results)
        avg_val = round(total_val / len(results), 2)
        min_val = min(r.score.value for r in results)
        max_val = max(r.score.value for r in results)

        return PerformanceMetric(
            total_score=Score(round(total_val, 2), unit),
            average_score=Score(avg_val, unit),
            highest_score=Score(max_val, unit),
            lowest_score=Score(min_val, unit),
            sample_size=len(results),
        )

    def build_ranking_table(self, sport_name: str, strategy: RankingStrategy | None = None) -> RankingTable:
        """Create a ranking table container applying the appropriate ranking strategy."""
        results = self.find_by_sport(sport_name)
        if not strategy and results:
            strategy = HigherScoreWinsStrategy() if results[0].sport.higher_is_better else LowerTimeWinsStrategy()
        selected_strategy = strategy or HigherScoreWinsStrategy()

        table = RankingTable(title=f"Рейтинг дисципліни '{sport_name}'", strategy=selected_strategy)
        for r in results:
            table.add(r)
        return table

    def export_report(self, sport_name: str) -> str:
        """Generate and export formatted report via injected ResultExporter."""
        table = self.build_ranking_table(sport_name)
        content_lines = [f"- {idx}. {res.athlete.name}: {res.score} ({res.category.value})" for idx, res in enumerate(table, start=1)]
        content = "\n".join(content_lines) if content_lines else "Немає зареєстрованих результатів."
        return self._exporter.export(title=table.title, content=content)
