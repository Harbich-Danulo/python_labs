"""Модульні тести для SportsAccountingService із використанням Mock та перевіркою взаємодії."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
import pytest

from sports_accounting.config import AppConfig
from sports_accounting.exceptions import RecordValidationError, RepositoryError
from sports_accounting.models import Athlete, Competition, Result, Sport
from sports_accounting.protocols import Notifier, ResultRepository
from sports_accounting.repositories import InMemoryResultRepository
from sports_accounting.services import SportsAccountingService
from sports_accounting.value_objects import Score


class TestSportsAccountingService:
    """Тести бізнес-логіки та взаємодії між компонентами (Mocking & Interactions)."""

    @pytest.fixture
    def mock_notifier(self) -> Mock:
        return Mock(spec=Notifier)

    @pytest.fixture
    def service_with_mocks(
        self,
        mock_notifier: Mock,
        sample_config: AppConfig,
    ) -> tuple[SportsAccountingService, InMemoryResultRepository, Mock]:
        repo = InMemoryResultRepository()
        service = SportsAccountingService(
            repository=repo,
            notifier=mock_notifier,
            config=sample_config,
        )
        return service, repo, mock_notifier

    def test_register_result_success_interaction(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        sample_result: Result,
    ) -> None:
        service, repo, mock_notifier = service_with_mocks

        # Act
        service.register_result(sample_result)

        # Assert state
        assert repo.count() == 1
        assert repo.get(sample_result.id) == sample_result

        # Assert interaction (Task 41 & 53)
        mock_notifier.send.assert_called_once()
        expected_msg = (
            f"Новий результат: {sample_result.athlete.name} — {sample_result.score} "
            f"({sample_result.sport.name}, {sample_result.category})"
        )
        mock_notifier.send.assert_called_once_with("admin@sports.ua", expected_msg)

    def test_register_duplicate_result_failure_path(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        sample_result: Result,
    ) -> None:
        service, repo, mock_notifier = service_with_mocks
        service.register_result(sample_result)
        mock_notifier.send.reset_mock()

        # Повторна реєстрація того самого ID повинна викликати RepositoryError
        with pytest.raises(RepositoryError, match="вже існує у сховищі"):
            service.register_result(sample_result)

        # Перевірка failure path: notifier НЕ повинен викликатися повторно
        mock_notifier.send.assert_not_called()

    def test_repository_side_effect_aborts_notification(
        self,
        sample_config: AppConfig,
        mock_notifier: Mock,
        sample_result: Result,
    ) -> None:
        mock_repo = Mock(spec=ResultRepository)
        # Налаштовуємо side_effect винятку (Task 40 & 70)
        mock_repo.add.side_effect = RepositoryError("Помилка дискового сховища")

        service = SportsAccountingService(
            repository=mock_repo,
            notifier=mock_notifier,
            config=sample_config,
        )

        with pytest.raises(RepositoryError, match="Помилка дискового сховища"):
            service.register_result(sample_result)

        # Перевірка: сповіщення НЕ надсилалося при збої репозиторію
        mock_notifier.send.assert_not_called()

    def test_find_best_result_higher_score(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        sample_sport_high_jump: Sport,
        sample_results_list: list[Result],
    ) -> None:
        service, repo, _ = service_with_mocks
        for r in sample_results_list:
            repo.add(r)

        best = service.find_best_result(sample_sport_high_jump.name)
        assert best is not None
        assert best.athlete.name == "Ярослава Магучіх"
        assert best.score.value == pytest.approx(2.10)

    def test_find_best_result_lower_time_swimming(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        sample_sport_swimming: Sport,
        sample_competition: Competition,
    ) -> None:
        service, repo, _ = service_with_mocks
        a1 = Athlete(1, "Михайло Романчук")
        a2 = Athlete(2, "Олександр Желтяков")
        r1 = Result(10, a1, sample_sport_swimming, sample_competition, Score(461.50, "s"), "Дорослі", datetime(2024, 1, 1))
        r2 = Result(11, a2, sample_sport_swimming, sample_competition, Score(472.10, "s"), "Юніори", datetime(2024, 1, 1))
        repo.add(r1)
        repo.add(r2)

        best = service.find_best_result("Плавання 800м")
        assert best is not None
        # Для плавання менший час є кращим
        assert best.athlete.name == "Михайло Романчук"
        assert best.score.value == pytest.approx(461.50)

    def test_find_best_result_empty_returns_none(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
    ) -> None:
        service, _, _ = service_with_mocks
        assert service.find_best_result("Неіснуючий вид") is None

    def test_calculate_average_score(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        sample_sport_high_jump: Sport,
        sample_results_list: list[Result],
    ) -> None:
        service, repo, _ = service_with_mocks
        for r in sample_results_list:
            repo.add(r)

        # Результати: 2.10, 2.00, 1.95, 1.95 -> сума = 8.00 / 4 = 2.00
        avg = service.calculate_average_score("Стрибки у висоту")
        assert avg == pytest.approx(2.00)

    def test_calculate_average_score_empty_returns_zero(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
    ) -> None:
        service, _, _ = service_with_mocks
        assert service.calculate_average_score("Стрибки у висоту") == pytest.approx(0.0)

    def test_build_ranking_table_service(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        sample_results_list: list[Result],
    ) -> None:
        service, repo, _ = service_with_mocks
        for r in sample_results_list:
            repo.add(r)

        table = service.build_ranking_table("Стрибки у висоту")
        assert len(table) == 4
        assert table[0].rank == 1
        assert table[0].result.athlete.name == "Ярослава Магучіх"

    def test_build_ranking_table_empty(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
    ) -> None:
        service, _, _ = service_with_mocks
        table = service.build_ranking_table("Порожній вид")
        assert len(table) == 0

    def test_import_from_csv_tolerant_mode(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        tmp_path: Path,
    ) -> None:
        service, repo, _ = service_with_mocks
        csv_file = tmp_path / "test_import.csv"
        csv_file.write_text(
            "id,athlete_id,athlete,age,country,sport_id,sport,unit,is_lower_better,competition_id,competition,location,year,result,category,timestamp\n"
            "1,101,Ярослава Магучіх,22,Україна,1,Стрибки у висоту,m,false,1,ЧУ,Львів,2024,2.10,Дорослі,2024-07-07T18:30:00\n"
            "2,102,,22,Україна,1,Стрибки у висоту,m,false,1,ЧУ,Львів,2024,2.00,Дорослі,2024-07-07T18:30:00\n"  # missing athlete
            "3,103,Ірина Геращенко,29,Україна,1,Стрибки у висоту,m,false,1,ЧУ,Львів,2024,2.00,Дорослі,2024-07-07T18:30:00\n",
            encoding="utf-8",
        )

        valid_cnt, invalid_cnt = service.import_from_csv(csv_file, skip_invalid=True)
        assert valid_cnt == 2
        assert invalid_cnt == 1
        assert repo.count() == 2

    def test_import_from_csv_strict_mode_raises(
        self,
        service_with_mocks: tuple[SportsAccountingService, InMemoryResultRepository, Mock],
        tmp_path: Path,
    ) -> None:
        service, repo, _ = service_with_mocks
        csv_file = tmp_path / "test_strict.csv"
        csv_file.write_text(
            "id,athlete_id,athlete,age,country,sport_id,sport,unit,is_lower_better,competition_id,competition,location,year,result,category,timestamp\n"
            "1,101,Ярослава Магучіх,22,Україна,1,Стрибки у висоту,m,false,1,ЧУ,Львів,2024,2.10,Дорослі,2024-07-07T18:30:00\n"
            "2,102,,22,Україна,1,Стрибки у висоту,m,false,1,ЧУ,Львів,2024,2.00,Дорослі,2024-07-07T18:30:00\n",
            encoding="utf-8",
        )

        with pytest.raises(RecordValidationError):
            service.import_from_csv(csv_file, skip_invalid=False)
        assert repo.count() == 1
