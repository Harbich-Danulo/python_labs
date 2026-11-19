# Лабораторна робота №8: Мережеве та асинхронне програмування. REST API

**Варіант №9: Облік спортивних результатів**

## 1. Опис проєкту
Проєкт реалізує сучасний асинхронний REST API для предметної області «Облік спортивних результатів» на базі фреймворку **FastAPI**, валідації **Pydantic v2**, ORM **SQLAlchemy 2.0**, та мережевого клієнта **HTTPX** з підтримкою асинхронного програмування (`asyncio`):
- **REST API:** повний набір ендпоінтів для операцій CRUD над ресурсами `athletes`, `sports`, `results`.
- **Аналітичні ендпоінти:** розрахунок найкращого результату, середнього бала дисципліни (`AVG`), агрегатних показників (`COUNT`, `MIN`, `MAX`) та формування відсортованого турнірного рейтингу.
- **Асинхронне агрегування даних:** паралельне отримання рейтингів кількох дисциплін за допомогою `asyncio.Task` та `asyncio.gather()`.
- **Контроль паралелізму та стійкість:** обмеження кількості одночасних мережевих викликів через `asyncio.Semaphore`, налаштування лімітів часу виконання (`timeout`) та механізм повторних спроб (`retry`) з експоненційною затримкою (exponential backoff).
- **Архітектура шарів:** чисте розділення між презентаційним рівнем (FastAPI endpoints), схемами передачі даних (Pydantic DTO), бізнес-логікою (Service Layer) та рівнем доступу до даних (Repository Layer / SQLite).

## 2. Структура проєкту (src-layout)
```text
Lab_08/
├── pyproject.toml                # Специфікація проекту, залежності та налаштування pytest/mypy
├── README.md                     # Документація користувача
├── REPORT.md                     # Академічний звіт (33 розділи, 50 питань)
├── report.html                   # HTML-версія для компіляції в PDF
├── Звіт_Лабораторна_8_Гарбіч.pdf # Фінальний офіційний звіт
├── data/
│   └── sports.db                 # Файл бази даних SQLite
├── src/
│   └── sports_api/
│       ├── __init__.py           # Пакет sports_api
│       ├── api.py                # FastAPI додаток, ендпоінти, обробники помилок
│       ├── schemas.py            # Pydantic моделі запитів, відповідей та валідації
│       ├── database.py           # Налаштування Engine, SessionLocal, Dependency Injection
│       ├── models.py             # ORM-моделі SQLAlchemy 2.0 (Sport, Athlete, Result)
│       ├── repositories.py       # Persistence layer (Repository Pattern)
│       ├── services.py           # Сервісний шар: бізнес-правила, розрахунки, валідація
│       ├── external_api.py       # Асинхронний клієнт (HTTPX, Task, gather, Semaphore, retry)
│       ├── main.py               # Запуск Uvicorn-сервера та наповнення даними
│       └── py.typed              # Маркер статичної типізації PEP 561
└── tests/
    ├── __init__.py
    ├── conftest.py               # Фікстури pytest (SQLite in-memory, TestClient, AsyncClient)
    ├── test_api.py               # Синхронні тести REST ендпоінтів
    ├── test_async_client.py      # Асинхронні тести клієнта, gather, Semaphore, timeout, retry
    ├── test_main.py              # Тести точки входу
    └── test_repositories.py      # Тести репозиторіїв бази даних
```

## 3. Встановлення та запуск

### 3.1. Встановлення залежностей
```bash
pip install -e .[dev]
```

### 3.2. Запуск REST API сервера
```bash
python -m sports_api.main
```
Сервер буде доступний за адресою: `http://127.0.0.1:8000`  
Інтерактивна документація Swagger UI: `http://127.0.0.1:8000/docs`  
Альтернативна документація ReDoc: `http://127.0.0.1:8000/redoc`

### 3.3. Запуск автоматизованих тестів
```bash
pytest -v
```

### 3.4. Перевірка типізації
```bash
python -m mypy src tests
```
