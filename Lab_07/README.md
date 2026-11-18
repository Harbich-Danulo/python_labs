# Лабораторна робота №7: Робота з базами даних у Python

**Варіант №9: Облік спортивних результатів**

## 1. Опис проєкту
Проєкт реалізує повноцінний persistence layer на базі реляційної СУБД SQLite для предметної області «Облік спортивних результатів». Архітектура побудована за принципами багатошаровості (Clean Architecture):
- **Domain Models & ORM:** декларативні моделі SQLAlchemy 2.0 (`Sport`, `Athlete`, `Result`).
- **Persistence Layer (Repository Pattern):** репозиторії `SportRepository`, `AthleteRepository`, `ResultRepository`.
- **Service Layer (Business Logic):** сервіс `SportsService`, що забезпечує валідацію, обчислення аналітичних показників та транзакційні операції з дотриманням ACID.
- **Python DB-API (sqlite3):** низькорівнева робота з базою даних, виконання безпечних параметризованих SQL-запитів проти SQL Injection та агрегатні запити (`COUNT`, `AVG`, `MIN`, `MAX`).
- **Database Migrations:** система міграцій на базі **Alembic** (додавання поля `competition_name` до таблиці `results`).
- **Integration Testing:** повний набір автоматизованих тестів на базі **pytest** з використанням SQLite in-memory бази даних.

## 2. Структура проєкту (src-layout)
```text
Lab_07/
├── alembic.ini                   # Конфігурація системи міграцій Alembic
├── pyproject.toml                # Метадані проєкту, залежності та конфігурація інструментів
├── README.md                     # Документація проєкту
├── REPORT.md                     # Повний звіт до лабораторної роботи
├── report.html                   # HTML-версія звіту для експорту в PDF
├── Звіт_Лабораторна_7_Гарбіч.pdf # Фінальний офіційний PDF-звіт
├── data/                         # Каталог робочої бази даних SQLite
│   └── sports.db
├── migrations/                   # Каталог міграцій Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_add_competition_name.py
├── src/
│   └── sports_db/
│       ├── __init__.py
│       ├── database.py           # Підключення до БД, Engine, SessionLocal, session_scope
│       ├── db_api.py             # Прямі параметризовані SQL-запити через sqlite3 DB-API
│       ├── models.py             # ORM-моделі SQLAlchemy (Base, Sport, Athlete, Result)
│       ├── repositories.py       # Реалізація Repository Pattern (CRUD для сутностей)
│       ├── services.py           # Сервісний шар: бізнес-правила, транзакції, аналітика
│       ├── main.py               # Точка входу, демонстрація роботи та CLI
│       └── py.typed
└── tests/                        # Інтеграційні тести
    ├── __init__.py
    ├── conftest.py               # Фікстури pytest (SQLite in-memory, тестові сесії)
    ├── test_repositories.py      # Тести CRUD-операцій та зв'язків моделей
    └── test_services.py          # Тести сервісів, транзакцій (ACID rollback) та DB-API
```

## 3. Встановлення та запуск

### 3.1. Встановлення залежностей
```bash
pip install -e .[dev]
```

### 3.2. Застосування міграцій Alembic
```bash
alembic upgrade head
```

### 3.3. Запуск демонстраційного застосунку
```bash
python -m sports_db.main
```

### 3.4. Запуск інтеграційних тестів та аналізу покриття
```bash
pytest -v
```

### 3.5. Перевірка типізації mypy
```bash
python -m mypy src tests
```
