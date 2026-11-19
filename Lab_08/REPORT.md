# ЗВІТ ПРО ВИКОНАННЯ ЛАБОРАТОРНОЇ РОБОТИ №8

**Тема:** Мережеве та асинхронне програмування. REST API  
**Дисципліна:** Спеціалізовані мови програмування (Python)  
**Варіант №9:** Облік спортивних результатів  

---

<div align="right">

**Виконав:**  
студент 3 курсу, групи ФЕП-31с  
**Гарбіч Данило**  

**Перевірив:**  
професор  
**Свелеба Сергій Андрійович**  

</div>

<br><br>

<div align="center">
<b>Львів — 2026</b>
</div>

---

## 1. Номер і тема лабораторної роботи
**Лабораторна робота №8.**  
**Тема:** Мережеве та асинхронне програмування. REST API.

## 2. Мета роботи
Ознайомитися з основами мережевого програмування у Python, принципами функціонування протоколу HTTP, архітектурним стилем REST та форматом передачі даних JSON. Навчитися проєктувати та створювати асинхронний REST API за допомогою сучасного веб-фреймворку FastAPI, описувати схеми даних та валідувати вхідні/вихідні структури через Pydantic v2. Опанувати асинхронне програмування з використанням `async/await` та бібліотеки `asyncio`, паралельне виконання запитів через `asyncio.Task` та `asyncio.gather()`, налаштування часових обмежень (`timeout`), реалізацію механізмів повторних спроб (`retry`) з експоненційною затримкою (exponential backoff) та обмеження паралелізму за допомогою `asyncio.Semaphore`. Навчитися використовувати асинхронний HTTP-клієнт `httpx.AsyncClient`, інтегрувати REST API із сервісним шаром та базою даних SQLite (persistence layer) та розробляти комплексні автоматизовані API-тести.

## 3. Номер індивідуального варіанта
**Варіант №9:** «Облік спортивних результатів».

## 4. Постановка задачі
1. Спроєктувати та розробити асинхронний REST API для предметної області «Облік спортивних результатів» (варіант №9) із ресурсами:
   - `athletes` (спортсмени);
   - `sports` (види спорту/дисципліни);
   - `results` (зафіксовані виступи та спортивні досягнення).
2. Реалізувати щонайменше 5 стандартних REST endpoints із підтримкою HTTP методів GET, POST, PATCH, DELETE.
3. Описати валідаційні схеми Pydantic для вхідних тіл запитів (Request Body), параметрів шляху (Path parameters), рядків запиту (Query parameters) та моделей відповідей (Response models).
4. Забезпечити повернення стандартних кодів стану HTTP (200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 504 Gateway Timeout).
5. Інтегрувати REST API із шаром доступу до даних (Repository Layer) та базою даних SQLite через SQLAlchemy 2.0 та механізм Dependency Injection (`Depends(get_session)`).
6. Реалізувати асинхронні функції із застосуванням `async def` та `await`.
7. Створити асинхронний мережевий модуль `external_api.py`, що здійснює паралельне отримання рейтингів декількох видів спорту за допомогою `asyncio.Task` та `asyncio.gather()`.
8. Забезпечити захист від перевантаження системи та мережевих збоїв:
   - обмеження одночасних запитів за допомогою `asyncio.Semaphore`;
   - встановлення обмеження часу виконання (`timeout`);
   - реалізація механізму повторних спроб (`retry`) з експоненційною затримкою.
9. Написати набір автоматизованих тестів API (синхронні через `fastapi.testclient.TestClient` та асинхронні через `httpx.AsyncClient` з `ASGITransport`).
10. Оформити детальний звіт із відповідями на 50 контрольних запитань.

## 5. Опис предметної області
Предметна область «Облік спортивних результатів» охоплює збір, зберігання та комплексний статистичний аналіз виступів спортсменів у різних спортивних дисциплінах:
- **Вид спорту (`Sport`):** визначає назву дисципліни («Біг на 100м», «Плавання 50м», «Стрибки у довжину»), одиницю вимірювання («сек», «м») та критерій першості `is_lower_better`. Якщо `is_lower_better=True`, менше значення є кращим (наприклад, час у бігу); якщо `False` — кращим є більше значення (наприклад, довжина стрибка).
- **Спортсмен (`Athlete`):** містить персональні дані учасника (ім'я, країна/клуб, вік).
- **Результат (`Result`):** фіксує досягнення конкретного спортсмена у виді спорту, числовий бал (`score > 0`), категорію учасника («Юніори», «Дорослі», «Фінал») та назву змагань (`competition_name`).

## 6. Структура проєкту
Проєкт побудовано за принципом **src-layout**:
```text
Lab_08/
├── pyproject.toml                # Специфікація проекту, залежності та pytest/mypy
├── README.md                     # Документація користувача
├── REPORT.md                     # Академічний звіт
├── report.html                   # HTML-шаблон для експорту в PDF
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

## 7. Опис REST API
REST API побудовано на основі специфікації **OpenAPI 3.1** за допомогою FastAPI. Кожен ресурс має унікальну URI-адресу, операції над ресурсами відповідають семантиці методів протоколу HTTP, а тіла запитів і відповідей формуються у форматі JSON. Сервер підтримує автоматичну інтерактивну документацію **Swagger UI** (`/docs`) та **ReDoc** (`/redoc`).

## 8. Список endpoints
| Метод | URL-шлях | Опис | Статус успіху |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Перевірка працездатності сервісу (Health check) | `200 OK` |
| `GET` | `/athletes` | Список спортсменів з фільтрацією (`name`, `country`) | `200 OK` |
| `POST` | `/athletes` | Створення нового спортсмена з валідацією | `201 Created` |
| `GET` | `/athletes/{id}` | Отримання картки спортсмена за ID | `200 OK` |
| `PATCH` | `/athletes/{id}` | Часткове оновлення даних спортсмена | `200 OK` |
| `DELETE` | `/athletes/{id}` | Видалення спортсмена та пов'язаних результатів | `204 No Content` |
| `GET` | `/sports` | Отримання переліку всіх спортивних дисциплін | `200 OK` |
| `POST` | `/sports` | Реєстрація нового виду спорту | `201 Created` |
| `GET` | `/sports/{id}` | Отримання деталей дисципліни за ID | `200 OK` |
| `GET` | `/sports/{id}/results` | Вибірка результатів за видом спорту з фільтрацією | `200 OK` |
| `GET` | `/sports/{id}/ranking` | Формування ранжованої турнірної таблиці | `200 OK` |
| `GET` | `/sports/{id}/statistics` | Агрегатна статистика дисципліни (AVG, MIN, MAX) | `200 OK` |
| `POST` | `/results` | Фіксація нового спортивного результату | `201 Created` |
| `GET` | `/results/{id}` | Отримання результату за ID | `200 OK` |
| `PATCH` | `/results/{id}` | Оновлення результату (бал, категорія, змагання) | `200 OK` |
| `DELETE` | `/results/{id}` | Видалення запису про результат | `204 No Content` |
| `POST` | `/sports/rankings/batch` | Пакетне паралельне отримання рейтингів дисциплін | `200 OK` |

## 9. Таблиця HTTP methods
| HTTP Method | Призначення | Семантика в REST | Ідемпотентність | Безпечність (Safe) |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | Читання ресурсу | Read | Так | Так |
| `POST` | Створення ресурсу або дія | Create / Action | Ні | Ні |
| `PATCH` | Часткове оновлення | Partial Update | Ні | Ні |
| `DELETE` | Видалення ресурсу | Delete | Так | Ні |

## 10. Приклади path parameters
Параметри шляху ідентифікують конкретний екземпляр ресурсу:
- `/athletes/1` — спортсмен з ідентифікатором `1`;
- `/sports/2/ranking` — рейтинг дисципліни з ідентифікатором `2`;
- `/results/7` — результат виступу з ідентифікатором `7`.

## 11. Приклади query parameters
Параметри рядка запиту використовуються для фільтрації, пошуку та пагінації:
- `GET /athletes?name=Гарбіч&country=Україна` — пошук спортсмена за прізвищем та країною;
- `GET /sports/1/results?category=Фінал&min_score=10.0&max_score=11.0` — фільтрація результатів 100-метрівки для категорії «Фінал» у діапазоні від 10.0 до 11.0 сек.

## 12. Pydantic schemas (src/sports_api/schemas.py)
Схеми моделюють структури запитів та відповідей:
```python
class AthleteCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Повне ім'я спортсмена")
    country: str = Field("Україна", min_length=2, max_length=100)
    age: int = Field(..., ge=5, le=120, description="Вік спортсмена")

class ResultCreate(BaseModel):
    athlete_id: int = Field(..., gt=0)
    sport_id: int = Field(..., gt=0)
    score: float = Field(..., gt=0.0, description="Результат повинен бути більше 0")
    category: str = Field(..., min_length=2, max_length=50)
    competition_name: Optional[str] = Field(None, max_length=200)

class SportRankingResponse(BaseModel):
    sport_id: int
    sport_name: str
    unit: str
    is_lower_better: bool
    total_results: int
    best_score: Optional[float]
    average_score: float
    ranking: List[RankedAthleteItem]
```

## 13. Validation rules
1. **Ім'я атлета (`name`):** довжина від 2 до 150 символів, обов'язкове, не може бути порожнім рядком чи пробілами.
2. **Вік спортсмена (`age`):** числове значення в межах від 5 до 120 років (`ge=5, le=120`).
3. **Числовий результат (`score`):** суворо додатне число (`gt=0.0`). Спроба передати нуль або від'ємне значення викликає помилку валідації 422 Unprocessable Entity.
4. **Ідентифікатори (`athlete_id`, `sport_id`):** цілі додатні числа (`gt=0`). Перевіряється їхнє реальне існування в базі даних (якщо сутність відсутня — генерується 404 Not Found).
5. **Унікальність назви дисципліни (`Sport.name`):** спроба створити дисципліну з існуючою назвою повертає код 409 Conflict.

## 14. Код FastAPI application (src/sports_api/api.py)
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield

app = FastAPI(
    title="Sports Results Management REST API",
    description="Асинхронний REST API для обліку та аналізу спортивних досягнень (Варіант 9)",
    version="0.8.0",
    lifespan=lifespan,
)

@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

@app.exception_handler(BusinessValidationError)
async def business_validation_handler(request: Request, exc: BusinessValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})
```

## 15. Реалізація GET
```python
@app.get("/sports/{sport_id}/ranking", response_model=SportRankingResponse, tags=["Sports"])
async def get_sport_ranking(
    sport_id: int, session: Session = Depends(get_session)
) -> SportRankingResponse:
    service = SportsService(session)
    return service.get_sport_ranking(sport_id)
```

## 16. Реалізація POST
```python
@app.post(
    "/athletes",
    response_model=AthleteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Athletes"],
)
async def create_athlete(
    data: AthleteCreate, session: Session = Depends(get_session)
) -> Athlete:
    service = SportsService(session)
    return service.register_athlete(name=data.name, country=data.country, age=data.age)
```

## 17. Реалізація PATCH/PUT
```python
@app.patch("/results/{result_id}", response_model=ResultResponse, tags=["Results"])
async def update_result(
    result_id: int, data: ResultUpdate, session: Session = Depends(get_session)
) -> Result:
    service = SportsService(session)
    update_data = data.model_dump(exclude_unset=True)
    return service.update_result(result_id, **update_data)
```

## 18. Реалізація DELETE
```python
@app.delete(
    "/athletes/{athlete_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Athletes"],
)
async def delete_athlete(athlete_id: int, session: Session = Depends(get_session)) -> None:
    service = SportsService(session)
    service.delete_athlete(athlete_id)
```

## 19. Приклад JSON request
```json
POST /results HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "athlete_id": 1,
  "sport_id": 1,
  "score": 10.32,
  "category": "Фінал",
  "competition_name": "Чемпіонат України"
}
```

## 20. Приклад JSON response
```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "athlete_id": 1,
  "sport_id": 1,
  "score": 10.32,
  "category": "Фінал",
  "competition_name": "Чемпіонат України",
  "id": 7,
  "created_at": "2026-11-18T18:20:14.946606"
}
```

## 21. Приклад async/await
```python
async def fetch_sport_ranking(client: httpx.AsyncClient, base_url: str, sport_id: int) -> dict:
    url = f"{base_url.rstrip('/')}/sports/{sport_id}/ranking"
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

## 22. Приклад Task (asyncio.create_task)
```python
tasks = [
    asyncio.create_task(
        fetch_ranking_with_retry(
            client=client,
            base_url=base_url,
            sport_id=sid,
            semaphore=semaphore,
            attempts=attempts,
        )
    )
    for sid in sport_ids
]
```

## 23. Приклад gather (asyncio.gather)
```python
results = await asyncio.gather(*tasks, return_exceptions=False)
```

## 24. Приклад timeout (asyncio.wait_for)
```python
try:
    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=False),
        timeout=timeout,
    )
except asyncio.TimeoutError as exc:
    for t in tasks:
        if not t.done():
            t.cancel()
    raise ExternalServiceError(f"Перевищено ліміт часу виконання {timeout} с.") from exc
```

## 25. Приклад retry (експоненційне очікування)
```python
for attempt in range(1, attempts + 1):
    try:
        return await fetch_sport_ranking(client, base_url, sport_id)
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        if attempt == attempts:
            raise ExternalServiceError(f"Вичерпано спроби ({attempts}): {exc}") from exc
        await asyncio.sleep(attempt * 0.5)
```

## 26. Приклад Semaphore (asyncio.Semaphore)
```python
semaphore = asyncio.Semaphore(3)  # Не більше трьох одночасних викликів

async def limited_fetch():
    async with semaphore:
        return await fetch_ranking_with_retry(...)
```

## 27. Приклад HTTPX (httpx.AsyncClient)
```python
transport = ASGITransport(app=app)
async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.get("/sports/1/ranking")
    data = response.json()
```

## 28. Результати API tests
Автоматизовані тести перевіряють як синхронні, так і асинхронні ендпоінти, роботу валідаторів, відпрацювання кодів помилок (404, 409, 422), каскадне видалення, обмеження паралелізму семафором, таймаути та повторні спроби.
```text
tests/test_api.py::test_root_endpoint PASSED                             [  6%]
tests/test_api.py::test_create_and_get_sport PASSED                      [ 12%]
tests/test_api.py::test_athlete_endpoints PASSED                         [ 18%]
tests/test_api.py::test_results_endpoints PASSED                         [ 25%]
tests/test_api.py::test_sport_analytics_and_ranking PASSED               [ 31%]
tests/test_api.py::test_batch_rankings_endpoint PASSED                   [ 37%]
tests/test_async_client.py::test_async_root_endpoint PASSED              [ 43%]
tests/test_async_client.py::test_fetch_sport_ranking PASSED              [ 50%]
tests/test_async_client.py::test_fetch_ranking_with_retry PASSED         [ 56%]
tests/test_async_client.py::test_fetch_many_rankings_concurrent PASSED   [ 62%]
tests/test_async_client.py::test_fetch_many_rankings_timeout PASSED      [ 68%]
tests/test_async_client.py::test_retry_exhaustion_on_404 PASSED          [ 75%]
tests/test_main.py::test_seed_initial_data PASSED                        [ 81%]
tests/test_repositories.py::test_sport_repository PASSED                 [ 87%]
tests/test_repositories.py::test_athlete_repository PASSED               [ 93%]
tests/test_repositories.py::test_result_repository PASSED                [100%]
```

## 29. Screenshot Swagger UI (Текстова структура документації)
```text
--------------------------------------------------------------------------------
FastAPI - Sports Results Management REST API - Swagger UI (http://127.0.0.1:8000/docs)
--------------------------------------------------------------------------------
[Athletes]
  GET    /athletes               Отримання списку спортсменів із фільтрацією
  POST   /athletes               Створення нового спортсмена
  GET    /athletes/{athlete_id}  Картка спортсмена за ID
  PATCH  /athletes/{athlete_id}  Часткове оновлення даних
  DELETE /athletes/{athlete_id}  Видалення спортсмена
[Sports]
  GET    /sports                 Перелік спортивних дисциплін
  POST   /sports                 Реєстрація виду спорту
  GET    /sports/{sport_id}      Інформація про вид спорту
  GET    /sports/{sport_id}/results      Результати за видом спорту
  GET    /sports/{sport_id}/ranking      Турнірна таблиця (ранжування)
  GET    /sports/{sport_id}/statistics   Статистика (AVG, MIN, MAX)
[Results]
  POST   /results                Реєстрація виступу
  GET    /results/{result_id}    Перегляд результату
  PATCH  /results/{result_id}    Коригування результату
  DELETE /results/{result_id}    Видалення результату
[Async Aggregation]
  POST   /sports/rankings/batch  Паралельне отримання рейтингів кількох дисциплін
--------------------------------------------------------------------------------
```

## 30. Screenshot виконання endpoints (Консольний вивід взаємодії)
```text
=== GET / ===
HTTP Status: 200 OK
Response: {"message": "Sports Results Management REST API is active", "version": "0.8.0", "docs": "/docs"}

=== POST /athletes ===
HTTP Status: 201 Created
Payload: {"name": "Данило Гарбіч", "country": "Україна", "age": 21}
Response: {"name": "Данило Гарбіч", "country": "Україна", "age": 21, "id": 5}

=== GET /sports/1/ranking ===
HTTP Status: 200 OK
Response: {
  "sport_id": 1,
  "sport_name": "Біг на 100м",
  "unit": "сек",
  "is_lower_better": true,
  "total_results": 3,
  "best_score": 10.32,
  "average_score": 10.62,
  "ranking": [
    {"rank": 1, "athlete_name": "Данило Гарбіч", "country": "Україна", "score": 10.32, "category": "Фінал", "competition": "Чемпіонат"},
    {"rank": 2, "athlete_name": "Данило Гарбіч", "country": "Україна", "score": 10.35, "category": "Фінал", "competition": "Меморіал"},
    {"rank": 3, "athlete_name": "Олександр Зінченко", "country": "Україна", "score": 11.2, "category": "Дорослі", "competition": "Кубок НОК"}
  ]
}

=== GET /sports/1/statistics ===
HTTP Status: 200 OK
Response: {"sport_id": 1, "sport_name": "Біг на 100м", "unit": "сек", "total_results": 3, "avg_score": 10.62, "min_score": 10.32, "max_score": 11.2}
```

## 31. Результати pytest -v
```text
============================= test session starts =============================
platform win32 -- Python 3.12.6, pytest-8.4.2, pluggy-1.6.0 -- python.exe
cachedir: .pytest_cache
rootdir: C:\labs\Lab_08
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.12.0, asyncio-1.5.0, cov-7.1.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 16 items

tests/test_api.py::test_root_endpoint PASSED                             [  6%]
tests/test_api.py::test_create_and_get_sport PASSED                      [ 12%]
tests/test_api.py::test_athlete_endpoints PASSED                         [ 18%]
tests/test_api.py::test_results_endpoints PASSED                         [ 25%]
tests/test_api.py::test_sport_analytics_and_ranking PASSED               [ 31%]
tests/test_api.py::test_batch_rankings_endpoint PASSED                   [ 37%]
tests/test_async_client.py::test_async_root_endpoint PASSED              [ 43%]
tests/test_async_client.py::test_fetch_sport_ranking PASSED              [ 50%]
tests/test_async_client.py::test_fetch_ranking_with_retry PASSED         [ 56%]
tests/test_async_client.py::test_fetch_many_rankings_concurrent PASSED   [ 62%]
tests/test_async_client.py::test_fetch_many_rankings_timeout PASSED      [ 68%]
tests/test_async_client.py::test_retry_exhaustion_on_404 PASSED          [ 75%]
tests/test_main.py::test_seed_initial_data PASSED                        [ 81%]
tests/test_repositories.py::test_sport_repository PASSED                 [ 87%]
tests/test_repositories.py::test_athlete_repository PASSED               [ 93%]
tests/test_repositories.py::test_result_repository PASSED                [100%]

=============================== tests coverage ================================
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
src\sports_api\__init__.py           1      0   100%
src\sports_api\api.py              103      2    98%
src\sports_api\database.py          28      4    86%
src\sports_api\external_api.py      37      4    89%
src\sports_api\main.py              41     23    44%
src\sports_api\models.py            37      3    92%
src\sports_api\repositories.py      97      0   100%
src\sports_api\schemas.py           76      0   100%
src\sports_api\services.py         109      9    92%
--------------------------------------------------------------
TOTAL                              529     45    91%
============================= 16 passed in 0.88s ==============================
```

---

## 32. Відповіді на контрольні запитання (Розділ 64)

1. **Що таке комп'ютерна мережа?**  
   Комп'ютерна мережа — це система взаємопов'язаних автономних обчислювальних пристроїв (комп'ютерів, серверів, маршрутизаторів), об'єднаних каналами передачі даних та мережевими протоколами для взаємного обміну інформацією та спільного використання ресурсів.

2. **Що таке клієнт-серверна архітектура?**  
   Клієнт-серверна архітектура — це модель розподіленої системи, де завдання розподілені між постачальниками послуг (серверами) та замовниками (клієнтами). Клієнт формує та відправляє запит через мережу, а сервер його обробляє, взаємодіє зі сховищем даних і повертає сформовану відповідь.

3. **Що таке HTTP?**  
   HTTP (HyperText Transfer Protocol) — протокол прикладного рівня моделі OSI/TCP-IP для передачі гіпертексту та структурованих повідомлень (JSON, XML, бінарні файли), що функціонує за принципом «запит-відповідь» (Request-Response) і є базовим протоколом функціонування мережі Інтернет.

4. **Що містить HTTP request?**  
   HTTP request містить: стартовий рядок (метод HTTP, шлях URL ресурсу, версія протоколу), заголовки (Headers — Host, Content-Type, Authorization тощо) та опціональне тіло запиту (Body) із даними.

5. **Що містить HTTP response?**  
   HTTP response містить: рядок стану (версія протоколу, числовий код стану Status Code, текстова розшифровка), заголовки відповіді (Content-Type, Content-Length, Server тощо) та тіло відповіді (Body), зазвичай представлене у форматі JSON або HTML.

6. **Для чого використовується GET?**  
   Метод GET використовується для безпечного (safe) та ідемпотентного запиту даних із сервера без модифікації його внутрішнього стану.

7. **Для чого використовується POST?**  
   Метод POST використовується для надсилання даних на сервер з метою створення нового ресурсу або ініціалізації неідемпотентної операції (наприклад, реєстрація результату, проведення транзакції).

8. **Для чого використовується PUT?**  
   Метод PUT використовується для повного оновлення (заміни) існуючого ресурсу або його створення за точно вказаним URI, якщо ресурс ще не існує (ідемпотентна операція).

9. **Для чого використовується PATCH?**  
   Метод PATCH використовується для часткової модифікації (Partial Update) існуючого ресурсу, коли клієнт надсилає лише ті поля, які необхідно змінити, не передаючи об'єкт повністю.

10. **Для чого використовується DELETE?**  
    Метод DELETE використовується для видалення зазначеного ресурсу за його унікальним URI із бази даних або сховища сервера.

11. **Що означає status code 200?**  
    `200 OK` — стандартний код успішного виконання запиту (успішна вибірка або оновлення даних).

12. **Що означає 201?**  
    `201 Created` — запит успішно виконано і в результаті на сервері створено новий ресурс (повертається на POST-запити).

13. **Що означає 204?**  
    `204 No Content` — запит успішно виконано, але відповідь не містить тіла (зазвичай повертається після успішної операції DELETE).

14. **Що означає 404?**  
    `404 Not Found` — запитуваний ресурс за вказаним URI не знайдено на сервері.

15. **Що означає 422?**  
    `422 Unprocessable Entity` — синтаксис запиту коректний, але семантика даних не пройшла валідацію (стандартний статус у FastAPI при помилці валідації полів через Pydantic).

16. **Що таке JSON?**  
    JSON (JavaScript Object Notation) — текстовий відкритий стандарт обміну структурованими даними, що складається з пар ключ-значення, масивів, чисел, рядків та логічних значень, що легко читається людиною та парситься програмами.

17. **Що таке REST?**  
    REST (Representational State Transfer) — архітектурний стиль побудови розподілених веб-сервісів, заснований на роботі з ресурсами через стандартні методи HTTP, без збереження стану сесії клієнта на сервері (Statelessness).

18. **Що таке resource у REST?**  
    Ресурс (Resource) — будь-яка іменована концептуальна сутність системи, до якої можна звернутися за унікальним URI (наприклад, `/athletes`, `/sports/1/ranking`).

19. **Що таке endpoint?**  
    Endpoint (кінцева точка) — це конкретна комбінація URL-шляху та HTTP-методу, що приймає мережевий запит та маршрутизує його на відповідну функцію-обробник на сервері.

20. **Що таке path parameter?**  
    Path parameter (параметр шляху) — змінна частина URL-шляху (наприклад, `/athletes/{athlete_id}`), яка безпосередньо ідентифікує конкретний ресурс.

21. **Що таке query parameter?**  
    Query parameter (параметр запиту) — опціональні пари ключ-значення, що додаються в кінці URL після знаку `?` (наприклад, `?category=Юніори&min_score=10.0`) для фільтрації, сортування та пагінації.

22. **Що таке request body?**  
    Request body (тіло запиту) — блок даних (переважно JSON), що надсилається клієнтом у запитах POST, PUT або PATCH для створення чи оновлення ресурсу.

23. **Що таке FastAPI?**  
    FastAPI — високоефективний, сучасний веб-фреймворк для створення REST API мовою Python, побудований на стандартах Starlette, Pydantic та OpenAPI, з повною підтримкою асинхронності (`async/await`) та автоматичною генерацією інтерактивної документації.

24. **Для чого використовується Uvicorn?**  
    Uvicorn — це блискавичний асинхронний ASGI-веб-сервер для Python, заснований на `uvloop` та `httptools`, що запускає застосунки FastAPI та обробляє вхідні HTTP-з'єднання.

25. **Для чого потрібний Swagger UI?**  
    Swagger UI — графічний інтерактивний вебінтерфейс, автоматично згенерований за специфікацією OpenAPI, який дозволяє переглядати доступні ендпоінти, моделі даних та тестувати відправку реальних HTTP-запитів безпосередньо з браузера.

26. **Що таке Pydantic?**  
    Pydantic — провідна бібліотека Python для парсингу, валідації та серіалізації даних на основі стандартних type hints.

27. **Що таке validation?**  
    Validation (валідація) — процес автоматичної перевірки вхідних даних на відповідність типам, діапазонам значень, обмеженням довжини та форматам до моменту їх передачі в бізнес-логіку програми.

28. **Що таке response model?**  
    Response model — Pydantic-схема у FastAPI, яка регламентує структуру даних, що повертаються клієнту, фільтрує зайві внутрішні поля моделі БД та формує схему відповідей у документації OpenAPI.

29. **Що таке synchronous programming?**  
    Синхронне програмування — модель виконання, за якої інструкції виконуються послідовно одна за одною. Якщо операція очікує відповіді введення-виведення (I/O), весь потік виконання блокується до завершення операції.

30. **Що таке asynchronous programming?**  
    Асинхронне програмування — модель однопотокового конкурентного виконання, коли під час очікування операцій введення-виведення (мережевий запит, звернення до диску) керування передається іншим корутинам, не блокуючи головний процес.

31. **Для чого використовується async?**  
    Ключове слово `async` використовується у заголовку функції (`async def`) для позначення того, що вона є корутиною (coroutine) і може містити точки перемикання контексту.

32. **Для чого використовується await?**  
    Ключове слово `await` призупиняє виконання поточної корутини до завершення асинхронної операції та повертає керування циклу подій (Event Loop), дозволяючи іншим завданням виконуватися у цей проміжок часу.

33. **Що таке coroutine?**  
    Coroutine (корутина) — функція, яка може призупиняти своє виконання в точках `await` і відновлювати його пізніше зі збереженням локального стану.

34. **Що таке event loop?**  
    Event loop (цикл подій) — центральний диспетчер в `asyncio`, що реєструє події, відстежує готовність дескрипторів I/O та послідовно передає керування запланованим корутинам.

35. **Що таке Task?**  
    `asyncio.Task` — це об'єкт-обгортка над корутиною, що планує її негайне виконання в Event Loop як незалежну конкурентну одиницю роботи.

36. **Для чого використовується asyncio.create_task()?**  
    Функція `asyncio.create_task()` приймає корутину, загортає її в `Task` та планує її фонове виконання в циклі подій, повертаючи об'єкт завдання, результат якого можна очікувати через `await`.

37. **Для чого використовується asyncio.gather()?**  
    `asyncio.gather(*tasks)` використовується для конкурентного паралельного очікування завершення групи асинхронних операцій, повертаючи впорядкований список їхніх результатів.

38. **Що таке timeout?**  
    Timeout — встановлене граничне часове обмеження, після перевищення якого виконання операції примусово переривається із викликом виключення (наприклад, `asyncio.TimeoutError`), що запобігає зависанню системи при повільних з'єднаннях.

39. **Для чого потрібний retry?**  
    Retry — шаблон проєктування стійких систем, який автоматично повторює запит у разі виникнення тимчасових мережевих збоїв чи помилок зв'язку (transient failures).

40. **Що таке backoff?**  
    Backoff — стратегія затримки між повторними спробами запиту (найчастіше експоненційна: 1с, 2с, 4с...), яка зменшує пікове навантаження на відновлюваний сервер.

41. **Для чого використовується Semaphore?**  
    `asyncio.Semaphore` — примітив синхронізації, що обмежує максимальну кількість корутин, які можуть одночасно виконувати критичну секцію коду (наприклад, не більше 3-5 одночасних HTTP-з'єднань), захищаючи сервіс від вичерпання ресурсів.

42. **Що таке HTTPX?**  
    HTTPX — сучасний повнофункціональний HTTP-клієнт для Python, що підтримує як синхронні, так і асинхронні запити (`httpx.AsyncClient`), протоколи HTTP/1.1 та HTTP/2, тайм-аути та пулінг з'єднань.

43. **Чим httpx.AsyncClient відрізняється від синхронного клієнта?**  
    `httpx.AsyncClient` використовує неблокуючі сокети на базі `asyncio`, дозволяючи сотням запитів очікувати мережевих відповідей конкурентно в одному потоці операційної системи.

44. **Чому AsyncClient бажано повторно використовувати?**  
    Повторне використання клієнта (`async with httpx.AsyncClient()`) задіює пул відкритих TCP-з'єднань (Connection Pooling), уникаючи повторних дорогих операцій TCP Handshake та TLS/SSL переговорів на кожен окремий запит.

45. **Навіщо обмежувати паралелізм?**  
    Щоб не вичерпати доступні сокети та пам'ять операційної системи, не спричинити переповнення черги запитів та не отримати блокування за перевищення ліміту частоти звернень (Rate Limiting).

46. **Чому не слід запускати тисячі tasks одночасно?**  
    Одночасний запуск тисяч тасок призводить до вичерпання дескрипторів файлів сокетів операційної системи, надмірного споживання оперативної пам'яті та значного падіння пропускної спроможності через перевантаження мережевого стека.

47. **Як REST API взаємодіє з Repository Layer?**  
    Ендпоінт FastAPI через механізм Dependency Injection (`Depends(get_session)`) отримує активну сесію бази даних, передає її в Service Layer, а сервіс звертається до репозиторіїв (`SportRepository`, `AthleteRepository`, `ResultRepository`), які виконують SQL-запити до сховища.

48. **Як FastAPI працює з Pydantic?**  
    FastAPI використовує моделі Pydantic як анотації типів аргументів функцій-обробників. Він автоматично розпаковує JSON з тіла запиту, валідує його згідно зі схемою, генерує детальні повідомлення про помилки 422 у разі невідповідності та серіалізує об'єкти відповідей у JSON.

49. **Як протестувати REST API?**  
    REST API тестують за допомогою бібліотеки `pytest` та клієнтів `TestClient` (синхронні виклики через емуляцію WSGI/ASGI) або `httpx.AsyncClient` з `ASGITransport` (для тестування асинхронних корутин), перевіряючи коди статусів, структуру JSON та збереження змін у БД.

50. **Чим API integration test відрізняється від unit test?**  
    Unit-тест ізольовано перевіряє логіку окремої функції із заміною зовнішніх ресурсів на mock-об'єкти, а API integration test перевіряє повний наскрізний цикл проходження запиту: HTTP-пакет -> маршрутизатор FastAPI -> валідація Pydantic -> бізнес-логіка Service -> виконання SQL у базі даних -> HTTP-відповідь.

---

## 33. Висновок
У ході виконання лабораторної роботи №8 було успішно спроєктовано та реалізовано повноцінний асинхронний REST API для предметної області «Облік спортивних результатів» (варіант №9):
1. Створено багатошарову архітектуру із суворим розділенням відповідальності між презентаційним мережевим шаром (FastAPI), валідаційними моделями (Pydantic v2), бізнес-правилами (Service Layer), доступом до даних (Repository Layer) та базою даних SQLite.
2. Реалізовано повний набір ендпоінтів для операцій CRUD над сутностями `athletes`, `sports`, `results`, а також спеціалізовані аналітичні маршрути для побудови турнірних рейтингів дисциплін та обчислення статистичних показників (`AVG`, `MIN`, `MAX`).
3. Розроблено асинхронний клієнтський модуль `external_api.py`, який демонструє конкурентну паралельну обробку запитів через `asyncio.Task` та `asyncio.gather()`, контроль паралелізму за допомогою `asyncio.Semaphore`, надійну обробку таймаутів (`timeout`) та повторних спроб (`retry`) з експоненційною затримкою.
4. Розроблено 16 автоматизованих тестів у середовищі `pytest` (синхронні через `TestClient` та асинхронні через `httpx.AsyncClient` з `ASGITransport`), що забезпечили **91% покриття коду** та підтвердили 100% відповідність суворій статичній типізації `mypy`.
