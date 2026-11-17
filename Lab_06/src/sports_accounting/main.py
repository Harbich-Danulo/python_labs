"""Точка входу в програму обліку спортивних результатів."""

from pathlib import Path

from sports_accounting.config import load_config
from sports_accounting.repositories import InMemoryResultRepository
from sports_accounting.services import SportsAccountingService


class ConsoleNotifier:
    """Проста реалізація сповіщувача для консолі."""

    def send(self, recipient: str, message: str) -> None:
        print(f"[NOTIFICATION to {recipient}]: {message}")


def main() -> None:
    """Головна функція демонстрації роботи системи."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        print(f"Конфігураційний файл '{config_path}' відсутній.")
        return

    config = load_config(config_path)
    repo = InMemoryResultRepository()
    notifier = ConsoleNotifier()
    service = SportsAccountingService(repository=repo, notifier=notifier, config=config)

    print("=== СИСТЕМА ОБЛІКУ СПОРТИВНИХ РЕЗУЛЬТАТІВ ===")
    if config.input_path.exists():
        valid_cnt, invalid_cnt = service.import_from_csv(config.input_path, skip_invalid=True)
        print(f"Імпортовано: {valid_cnt} валідних, {invalid_cnt} некоректних записів.")

    table = service.build_ranking_table("Стрибки у висоту")
    print(f"Турнірна таблиця ({table.sport.name}): {len(table)} учасників.")
    for entry in table:
        print(f"  #{entry.rank}: {entry.result.athlete.name} — {entry.result.score}")


if __name__ == "__main__":
    main()
