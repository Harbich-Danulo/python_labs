"""Тестування точки входу main.py та демонстраційних сценаріїв."""

from unittest.mock import patch
from sqlalchemy.orm import Session
from sports_db.main import (
    demonstrate_acid_transaction,
    demonstrate_dbapi_queries,
    display_analytics_and_ranking,
    initialize_database,
    main,
    seed_sample_data,
)
from sports_db.services import SportsService


def test_main_execution(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Перевірка виконання головного сценарію main."""
    # Запускаємо main і перевіряємо, що вона проходить без помилок
    with patch("builtins.print") as mock_print:
        main()
        assert mock_print.called


def test_demonstration_components(populated_session: Session) -> None:
    service = SportsService(populated_session)
    # Тестуємо окремі функції
    demonstrate_acid_transaction(service)
    display_analytics_and_ranking(service)
