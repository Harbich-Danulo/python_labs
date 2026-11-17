# Система обліку спортивних результатів (Лабораторна робота №6)

Індивідуальний варіант №9: **«Система обліку спортивних результатів»**.

## Опис проєкту
Професійний Python-проєкт із повноцінним автоматизованим тестовим набором (unit та integration tests) на основі фреймворку `pytest`.
Проєкт охоплює:
- Доменні моделі (`Athlete`, `Sport`, `Competition`, `Score` value object, `Result`, `RankingTable`);
- Патерни проектування: Strategy, Dependency Injection, Repository, Protocols;
- Потоковий імпорт CSV, атомарний експорт JSON;
- Асинхронний провайдер зовнішніх результатів (`AsyncExternalResultsProvider`);
- Тестування з `fixtures`, `parametrize`, `pytest.raises`, `pytest.approx`, `tmp_path`, `monkeypatch`, `Mock`, `AsyncMock`, `side_effect`;
- Аналіз покриття коду тестами (`pytest-cov`) із підтримкою branch coverage.

## Встановлення залежностей
```bash
python -m pip install -e ".[dev]"
```

## Запуск тестів та перевірка покриття
```bash
pytest -v --cov=sports_accounting --cov-branch --cov-report=term-missing --cov-report=html
```
