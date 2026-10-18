"""Unit tests for Laboratory Work 4 domain models, repositories, and services."""

from sports_app.dto import ResultPayload
from sports_app.models import (
    Athlete,
    AthleteCategory,
    Competition,
    HigherScoreWinsStrategy,
    LowerTimeWinsStrategy,
    RankingTable,
    Result,
    Sport,
)
from sports_app.protocols import Identifiable, ScoredEntity
from sports_app.repositories import InMemoryRepository
from sports_app.services import (
    ConsoleNotifier,
    MarkdownExporter,
    SportsAccountingService,
)
from sports_app.value_objects import Score


def test_score_value_object() -> None:
    s1 = Score(2.10, "m")
    s2 = Score(0.05, "m")
    s3 = s1 + s2
    assert s3.value == 2.15
    assert s3.unit == "m"


def test_athlete_and_result() -> None:
    ath = Athlete(1, "Ярослава Магучіх", "Україна", 22)
    sport = Sport(10, "Стрибки у висоту", higher_is_better=True, default_unit="m")
    comp = Competition(100, "Diamond League", "Париж", 2024)
    res = Result(101, ath, sport, comp, Score(2.10, "m"), AthleteCategory.SENIORS)

    assert isinstance(ath, Identifiable)
    assert isinstance(res, ScoredEntity)
    assert res.score.value == 2.10


def test_ranking_table_dunder_methods() -> None:
    ath1 = Athlete(1, "Магучіх")
    ath2 = Athlete(2, "Геращенко")
    sport = Sport(10, "Стрибки у висоту")
    comp = Competition(100, "ЧУ", "Львів")

    r1 = Result(101, ath1, sport, comp, Score(2.10, "m"), AthleteCategory.SENIORS)
    r2 = Result(102, ath2, sport, comp, Score(2.00, "m"), AthleteCategory.SENIORS)

    table = RankingTable(title="Висота", strategy=HigherScoreWinsStrategy())
    table.add(r2)
    table.add(r1)

    assert len(table) == 2
    assert 101 in table
    assert table[0].id == 101  # Ranked first due to HigherScoreWinsStrategy
    assert [r.id for r in table] == [101, 102]


def test_service_with_dependency_injection() -> None:
    service = SportsAccountingService(
        athlete_repo=InMemoryRepository[Athlete](),
        result_repo=InMemoryRepository[Result](),
        notifier=ConsoleNotifier(),
        exporter=MarkdownExporter(),
    )

    payload: ResultPayload = {
        "result_id": 1,
        "athlete_id": 1,
        "athlete_name": "Ілля Ковтун",
        "country": "Україна",
        "age": 21,
        "sport_name": "Гімнастика",
        "competition_name": "Олімпіада",
        "location": "Париж",
        "year": 2024,
        "score_value": 15.65,
        "score_unit": "pts",
        "category": "Юніори",
    }

    res = service.register_result_from_payload(payload)
    assert res.athlete.name == "Ілля Ковтун"
    assert service.find_best_result("Гімнастика") is not None


if __name__ == "__main__":
    test_score_value_object()
    test_athlete_and_result()
    test_ranking_table_dunder_methods()
    test_service_with_dependency_injection()
    print("All Laboratory Work 4 tests passed successfully!")
