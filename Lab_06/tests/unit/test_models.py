"""Модульні тести доменних моделей, Value Objects та RankingTable."""

from datetime import datetime
import pytest

from sports_accounting.models import (
    Athlete,
    Competition,
    RankingTable,
    Result,
    Sport,
)
from sports_accounting.value_objects import Score


class TestScoreValueObject:
    """Тести для незмінного Value Object Score."""

    def test_score_creation_valid(self) -> None:
        # Arrange & Act
        score = Score(value=2.10, unit="m")
        # Assert
        assert score.value == pytest.approx(2.10)
        assert score.unit == "m"
        assert str(score) == "2.10 m"

    @pytest.mark.parametrize(
        "value",
        [-0.01, -1.0, -100.5],
        ids=["slight_negative", "unit_negative", "large_negative"],
    )
    def test_score_negative_rejected(self, value: float) -> None:
        with pytest.raises(ValueError, match="не може бути від'ємним"):
            Score(value=value, unit="m")

    def test_score_empty_unit_rejected(self) -> None:
        with pytest.raises(ValueError, match="Одиниця вимірювання"):
            Score(value=10.0, unit="   ")

    def test_score_addition_success(self) -> None:
        s1 = Score(2.10, "m")
        s2 = Score(0.05, "m")
        res = s1 + s2
        assert res.value == pytest.approx(2.15)
        assert res.unit == "m"

    def test_score_addition_mismatch_unit_raises(self) -> None:
        s1 = Score(2.10, "m")
        s2 = Score(15.0, "s")
        with pytest.raises(ValueError, match="Неможливо додати результати з різними одиницями"):
            _ = s1 + s2

    def test_score_subtraction_success(self) -> None:
        s1 = Score(2.10, "m")
        s2 = Score(0.10, "m")
        diff = s1 - s2
        assert diff.value == pytest.approx(2.00)

    def test_score_subtraction_negative_result_raises(self) -> None:
        s1 = Score(1.00, "m")
        s2 = Score(2.00, "m")
        with pytest.raises(ValueError, match="не може бути від'ємною"):
            _ = s1 - s2

    def test_score_comparisons(self) -> None:
        s1 = Score(1.95, "m")
        s2 = Score(2.10, "m")
        assert s1 < s2
        assert s2 > s1
        assert not (s1 > s2)


class TestDomainEntities:
    """Тести валідації сутностей Athlete, Sport, Competition, Result."""

    def test_athlete_valid(self) -> None:
        athlete = Athlete(id=1, name="Ярослава Магучіх", country="Україна", age=22)
        assert athlete.id == 1
        assert athlete.name == "Ярослава Магучіх"
        assert athlete.age == 22

    @pytest.mark.parametrize(
        ("age", "is_valid"),
        [
            (9, False),    # boundary below 10
            (10, True),    # boundary min
            (25, True),    # normal
            (100, True),   # boundary max
            (101, False),  # boundary above 100
        ],
        ids=["age_9", "age_10", "age_25", "age_100", "age_101"],
    )
    def test_athlete_age_boundary(self, age: int, is_valid: bool) -> None:
        if is_valid:
            a = Athlete(id=1, name="Атлет", age=age)
            assert a.age == age
        else:
            with pytest.raises(ValueError, match="Вік спортсмена повинен бути в межах"):
                Athlete(id=1, name="Атлет", age=age)

    def test_athlete_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="Ім'я спортсмена не може бути порожнім"):
            Athlete(id=1, name="   ", age=20)

    def test_athlete_negative_id_raises(self) -> None:
        with pytest.raises(ValueError, match="ID спортсмена повинен бути додатнім"):
            Athlete(id=0, name="Атлет", age=20)

    def test_sport_validation(self) -> None:
        sport = Sport(id=1, name="Плавання 800м", unit="s", is_lower_better=True)
        assert sport.is_lower_better is True
        with pytest.raises(ValueError, match="ID виду спорту повинен бути додатнім"):
            Sport(id=-1, name="Стрибки", unit="m")
        with pytest.raises(ValueError, match="Назва виду спорту не може бути порожньою"):
            Sport(id=1, name="", unit="m")

    def test_competition_year_boundaries(self) -> None:
        comp = Competition(id=1, name="Олімпіада", location="Париж", year=2024)
        assert comp.year == 2024
        with pytest.raises(ValueError, match="Рік змагання має бути в межах"):
            Competition(id=1, name="Античні ігри", location="Олімпія", year=1899)
        with pytest.raises(ValueError, match="Рік змагання має бути в межах"):
            Competition(id=1, name="Футуристичні ігри", location="Місяць", year=2101)

    def test_result_unit_mismatch_raises(
        self,
        sample_athlete: Athlete,
        sample_sport_high_jump: Sport,
        sample_competition: Competition,
    ) -> None:
        with pytest.raises(ValueError, match="не відповідає виду спорту"):
            Result(
                id=1,
                athlete=sample_athlete,
                sport=sample_sport_high_jump,  # unit="m"
                competition=sample_competition,
                score=Score(12.5, "s"),  # mismatch unit!
                category="Дорослі",
                timestamp=datetime(2024, 7, 7),
            )

    def test_result_to_dict_serialization(self, sample_result: Result) -> None:
        data = sample_result.to_dict()
        assert data["id"] == sample_result.id
        assert data["athlete"]["name"] == "Ярослава Магучіх"
        assert data["sport"]["name"] == "Стрибки у висоту"
        assert data["score"]["value"] == 2.10
        assert data["score"]["unit"] == "m"


class TestRankingTable:
    """Тести для контейнера RankingTable, включаючи правила ранжування та нічиї (ties)."""

    def test_ranking_higher_score_wins(
        self,
        sample_sport_high_jump: Sport,
        sample_results_list: list[Result],
    ) -> None:
        table = RankingTable(sample_sport_high_jump, sample_results_list)
        assert len(table) == 4

        # Перевірка перших двох позицій
        assert table[0].rank == 1
        assert table[0].result.athlete.name == "Ярослава Магучіх"
        assert table[0].result.score.value == 2.10

        assert table[1].rank == 2
        assert table[1].result.athlete.name == "Ірина Геращенко"
        assert table[1].result.score.value == 2.00

        # Перевірка нічиєї (ties): обидва атлети з результатом 1.95 повинні мати rank == 3!
        assert table[2].rank == 3
        assert table[2].result.score.value == 1.95

        assert table[3].rank == 3
        assert table[3].result.score.value == 1.95

    def test_ranking_lower_time_wins(
        self,
        sample_sport_swimming: Sport,
        sample_competition: Competition,
    ) -> None:
        a1 = Athlete(1, "Михайло Романчук")
        a2 = Athlete(2, "Олександр Желтяков")
        r1 = Result(1, a1, sample_sport_swimming, sample_competition, Score(461.5, "s"), "Дорослі", datetime(2024, 1, 1))
        r2 = Result(2, a2, sample_sport_swimming, sample_competition, Score(472.1, "s"), "Юніори", datetime(2024, 1, 1))

        table = RankingTable(sample_sport_swimming, [r2, r1])
        assert len(table) == 2
        # Менший час перемагає
        assert table[0].rank == 1
        assert table[0].result.athlete.name == "Михайло Романчук"
        assert table[1].rank == 2
        assert table[1].result.athlete.name == "Олександр Желтяков"

    def test_ranking_table_empty(self, sample_sport_high_jump: Sport) -> None:
        table = RankingTable(sample_sport_high_jump, [])
        assert len(table) == 0
        assert list(table) == []

    def test_ranking_table_dunder_methods(
        self,
        sample_sport_high_jump: Sport,
        sample_results_list: list[Result],
    ) -> None:
        table = RankingTable(sample_sport_high_jump, sample_results_list)

        # __contains__
        assert "Ярослава Магучіх" in table
        assert "Невідомий Атлет" not in table
        assert 123 not in table  # not a string

        # __iter__
        athletes = [entry.result.athlete.name for entry in table]
        assert "Ярослава Магучіх" in athletes

        # __repr__
        assert "RankingTable" in repr(table)
