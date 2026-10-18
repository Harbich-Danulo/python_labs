# ЗВІТ ПРО ВИКОНАННЯ ЛАБОРАТОРНОЇ РОБОТИ №5
**Тема:** Обробка помилок, файли та серіалізація  
**Курс:** Професійний Python  
**Індивідуальний варіант №9:** «Імпорт та експорт спортивних результатів»  

**Виконав:**  
студент 3 курсу, групи ФЕП-31с  
Гарбіч Данило  

**Перевірив:**  
професор  
Свелеба Сергій Андрійович  

**Львів — 2026**

---

## 1. Мета роботи
Сформувати практичні навички створення надійних Python-програм, які коректно працюють із помилками, файловими ресурсами, конфігурацією та структурованими форматами даних (CSV, JSON, YAML). Опанувати механізм exceptions, конструкції `try/except/else/finally`, власні ієрархії винятків із збереженням першопричини (exception chaining), принципи EAFP і fail-fast, context managers, потокову обробку (streaming I/O), атомарний запис файлів (atomic write) та промислове логування (`logging`).

---

## 2. Номер і тема лабораторної роботи
Лабораторна робота №5. «Обробка помилок, файли та серіалізація».

---

## 3. Номер індивідуального варіанта
Варіант №9: «Імпорт та експорт спортивних результатів».

---

## 4. Постановка задачі
Створити надійний production-ready модуль імпорту, валідації, фільтрації та експорту спортивних результатів відповідно до варіанта №9:
1. Працювати виключно через сучасний модуль `pathlib.Path`.
2. Реалізувати потокове читання даних (Streaming input через генератори) для запобігання переповненню RAM.
3. Підтримувати імпорт з CSV, JSON Lines та YAML через єдиний абстрактний інтерфейс (протокол `Importer`).
4. Забезпечити конфігурування конвеєра через зовнішній файл `config.yaml` із валідацією параметрів (fail-fast).
5. Побудувати domain-specific ієрархію винятків (`ApplicationError` -> `DataError` -> `RecordValidationError`).
6. Використати ланцюжки винятків (`raise ... from error`) для збереження першопричини низкорівневих помилок.
7. Реалізувати власний контекстний менеджер для транзакційності та профілювання часу операцій (`logged_operation`).
8. Налаштувати багаторівневе логування з очищенням чутливих даних.
9. Підтримувати дві політики надійності: `strict` (переривання при першій помилці) та `tolerant` (пропуск помилок із реєстрацією у звіті).
10. Реалізувати атомарний експорт (atomic write через `*.tmp` та атомарну заміну файлу), що запобігає пошкодженню цільових файлів при раптових збоях.
11. Зібрати статистику обробки (`total`, `valid`, `invalid`, `exported`) та сформувати окремий звіт про помилки.

---

## 5. Input data schema
Схема записів спортивних результатів (Варіант 9):
- `athlete` (`str`): Прізвище та ім'я спортсмена (непорожній рядок без провідних/кінцевих пробілів).
- `sport` (`str`): Назва спортивної дисципліни (повинна входити до списку `allowed_sports` із конфігурації).
- `result` (`float`): Числовий показник досягнення (висота у метрах, час у секундах або бали; перевіряється на відповідність діапазону `[min_value, max_value]` для конкретного виду спорту).
- `category` (`str`): Вікова/кваліфікаційна категорія («Дорослі», «Юніори», «Молодь», «Ветерани»).
- `timestamp` (`str` / `datetime`): Часова мітка фіксації рекорду у форматі ISO 8601 (не старіша за `min_timestamp`).

---

## 6. Приклад вхідного CSV (`data/sports_results.csv`)
```csv
athlete,sport,result,category,timestamp
Ярослава Магучіх,Стрибки у висоту,2.10,Дорослі,2024-07-07T18:30:00
Ірина Геращенко,Стрибки у висоту,2.00,Дорослі,2024-08-04T19:00:00
Юлія Левченко,Стрибки у висоту,1.95,Дорослі,2024-06-15T17:45:00
,Стрибки у висоту,1.90,Дорослі,2024-07-10T12:00:00
Ілля Ковтун,Спортивна гімнастика,15.65,Дорослі,2024-07-29T16:15:00
Олег Верняєв,Спортивна гімнастика,15.30,Дорослі,2024-07-29T16:30:00
Михайло Романчук,Плавання 800м,461.50,Дорослі,2024-07-30T11:20:00
Олександр Желтяков,Плавання 800м,472.10,Юніори,2024-07-30T11:25:00
Сергій Бубка,Стрибки у висоту,3.80,Ветерани,2024-05-10T14:00:00
Владислав Лавський,Стрибки з жердиною,5.80,Дорослі,2024-06-20T18:00:00
Артем Коваль,Біг 100м,invalid_num,Юніори,2024-08-10T10:00:00
Олена Старікова,Велоспорт,10.75,НевідомаКатегорія,2024-07-12T15:00:00
Марія Савченко,Стрільба з лука,680.00,Дорослі,2020-01-01T12:00:00
Андрій Проценко,Стрибки у висоту,2.25,Дорослі,2024-08-01T19:30:00
```

---

## 7. Структура проєкту
```text
reliable_sports_importer/
├── pyproject.toml
├── config.yaml
├── README.md
├── data/
│   └── sports_results.csv
├── output/
│   ├── sports_results.json
│   ├── error_report.json
│   └── error_report.csv
├── logs/
│   └── application.log
├── src/
│   └── reliable_sports_importer/
│       ├── __init__.py
│       ├── py.typed
│       ├── exceptions.py
│       ├── models.py
│       ├── config.py
│       ├── logging_config.py
│       ├── utils.py
│       ├── readers.py
│       ├── validators.py
│       ├── exporters.py
│       ├── services.py
│       └── main.py
└── tests/
    ├── test_sports_importer.py
    └── experiments_runner.py
```

---

## 8. Ієрархія винятків (`exceptions.py`)
```python
class ApplicationError(Exception):
    """Базовий виняток додатку."""

class ConfigurationError(ApplicationError):
    """Виникає при помилках конфігурації."""

class DataError(ApplicationError):
    """Базовий виняток для помилок обробки даних."""

class DataImportError(DataError):
    """Критичні помилки відкриття чи парсингу вхідного потоку."""

class RecordValidationError(DataError):
    """Помилка валідації окремого запису предметної області."""
    def __init__(self, message: str, *, line_number: int | None = None,
                 field: str | None = None, raw_value: Any = None) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.field = field
        self.raw_value = raw_value

class DataExportError(DataError):
    """Помилка атомарного експорту або серіалізації."""
```

---

## 9. Пояснення custom exceptions
Власна ієрархія винятків вирішує фундаментальну проблему архітектури — відокремлення технічних збоїв середовища від помилок бізнес-логіки. Клієнтський код конвеєра перехоплює суворо доменні винятки (`ApplicationError`, `DataError`), отримуючи збагачений контекст: номер проблемного рядка `line_number`, назву поля `field` та сире значення `raw_value`.

---

## 10. Приклад exception chaining
```python
result_raw = row.get("result")
try:
    result_val = float(result_raw)
except (TypeError, ValueError) as error:
    raise RecordValidationError(
        f"Результат має бути дійсним числовим значенням: {result_raw}",
        line_number=line_number,
        field="result",
        raw_value=result_raw,
    ) from error
```
Конструкція `from error` встановлює внутрішній атрибут `__cause__`, що гарантує збереження первинного низькорівневого трасування (traceback) для спрощення налагодження.

---

## 11. Вміст `config.yaml`
```yaml
input:
  path: data/sports_results.csv

output:
  path: output/sports_results.json
  error_report_path: output/error_report.json

processing:
  skip_invalid: true
  min_timestamp: "2024-01-01T00:00:00"
  allowed_sports:
    - "Стрибки у висоту"
    - "Плавання 800м"
    - "Спортивна гімнастика"
    - "Біг 100м"
    - "Стрільба з лука"
  allowed_categories:
    - "Дорослі"
    - "Юніори"
    - "Молодь"
    - "Ветерани"
  sport_rules:
    "Стрибки у висоту":
      min_value: 1.00
      max_value: 2.50
    "Плавання 800м":
      min_value: 400.00
      max_value: 800.00
    "Спортивна гімнастика":
      min_value: 10.00
      max_value: 16.50
    "Біг 100м":
      min_value: 9.50
      max_value: 20.00
    "Стрільба з лука":
      min_value: 0.00
      max_value: 720.00

logging:
  level: INFO
  path: logs/application.log
```

---

## 12. Код configuration loader та validation (`config.py`)
```python
def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise ConfigurationError(f"Конфігураційний файл не знайдено: {path}")
    try:
        with path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Синтаксична помилка YAML: {error}") from error

    # Парсинг секцій та валідація
    config = AppConfig(...)
    validate_config(config)
    return config

def validate_config(config: AppConfig) -> None:
    if not config.input_path.exists():
        raise ConfigurationError(f"Вхідний файл для обробки не знайдено: {config.input_path}")
    for sport, rule in config.processing.sport_rules.items():
        if rule.min_value > rule.max_value:
            raise ConfigurationError(f"Некоректний діапазон для {sport}")
```

---

## 13. Logging configuration (`logging_config.py`)
```python
def configure_logging(level: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(path, encoding="utf-8")
    stream_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers = [file_handler, stream_handler]
```

---

## 14. Фрагмент log file (`logs/application.log`)
```text
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | =================================================================
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | ЛАБОРАТОРНА РОБОТА №5: ОБРОБКА ПОМИЛОК, ФАЙЛИ ТА СЕРІАЛІЗАЦІЯ
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Варіант 9: Імпорт та експорт спортивних результатів
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Конфігурацію успішно завантажено з: config.yaml
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Режим обробки: Tolerant (skip_invalid=True)
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.utils | Початок операції: Sports Data Pipeline Processing
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 5: Ім'я спортсмена не може бути порожнім
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 10: Результат 3.8 виходить за межі допустимого діапазону [1.0, 2.5]
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 11: Вид спорту 'Стрибки з жердиною' не входить до переліку дозволених
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 12: Результат має бути дійсним числовим значенням: invalid_num
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 13: Вид спорту 'Велоспорт' не входить до переліку дозволених
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 14: Часова мітка 2020-01-01 є старішою за мінімально дозволену
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.services | Звіт про некоректні записи експортовано у output\error_report.json
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.utils | Операція 'Sports Data Pipeline Processing' успішно завершена за 0.004240 с
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | -----------------------------------------------------------------
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Всього прочитано записів: 14 | Валідних: 8 | Некоректних: 6 | Експортовано: 8
```

---

## 15. Streaming reader (`readers.py`)
```python
class CsvImporter:
    def read(self, path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                for line_number, row in enumerate(reader, start=2):
                    yield line_number, row
        except OSError as error:
            raise DataImportError(f"Помилка читання файлу: {error}") from error
```

---

## 16. Validation code (`validators.py`)
```python
def parse_and_validate_record(row: dict[str, Any], *, line_number: int, config: ProcessingConfig) -> SportsResult:
    athlete = str(row.get("athlete", "")).strip()
    if not athlete:
        raise RecordValidationError("Ім'я спортсмена не може бути порожнім", line_number=line_number, field="athlete")

    sport = str(row.get("sport", "")).strip()
    if sport not in config.allowed_sports:
        raise RecordValidationError(f"Вид спорту '{sport}' не дозволений", line_number=line_number, field="sport")

    try:
        res_val = float(row.get("result"))
    except (TypeError, ValueError) as err:
        raise RecordValidationError("Результат має бути числовим", line_number=line_number, field="result") from err

    rule = config.sport_rules.get(sport)
    if rule and not (rule.min_value <= res_val <= rule.max_value):
        raise RecordValidationError(f"Результат {res_val} поза межами [{rule.min_value}, {rule.max_value}]", line_number=line_number, field="result")

    return SportsResult(athlete=athlete, sport=sport, result=res_val, category=row["category"], timestamp=datetime.fromisoformat(row["timestamp"]))
```

---

## 17. Strict vs Tolerant processing
```python
for line_number, raw_row in importer.read(self.config.input_path):
    self.statistics.total_records += 1
    try:
        item = parse_and_validate_record(raw_row, line_number=line_number, config=self.config.processing)
    except RecordValidationError as error:
        self.statistics.invalid_records += 1
        self.invalid_records.append(InvalidRecordDetail(line_number, str(raw_row), str(error), error.field))
        logger.warning("Некоректний запис рядка %s: %s", line_number, error)
        if self.config.processing.skip_invalid:
            continue  # Tolerant mode
        raise  # Strict mode: негайне переривання
    self.statistics.valid_records += 1
    yield item
```

---

## 18. JSON serialization та Atomic export (`utils.py`, `exporters.py`)
```python
@contextmanager
def atomic_file_writer(target_path: Path, encoding: str = "utf-8") -> Iterator[Any]:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    try:
        with temp_path.open("w", encoding=encoding) as file:
            yield file
        temp_path.replace(target_path)  # Атомарна заміна
    except Exception as error:
        temp_path.unlink(missing_ok=True)
        raise DataExportError(f"Неможливо виконати атомарний запис у {target_path}: {error}") from error
```

---

## 19. Власний context manager (`utils.py`)
```python
@contextmanager
def logged_operation(operation_name: str) -> Iterator[None]:
    logger.info("Початок операції: %s", operation_name)
    start_time = perf_counter()
    try:
        yield
    except Exception as error:
        elapsed = perf_counter() - start_time
        logger.exception("Операція '%s' зазнала збою після %.6f с: %s", operation_name, elapsed, error)
        raise
    else:
        elapsed = perf_counter() - start_time
        logger.info("Операція '%s' успішно завершена за %.6f с", operation_name, elapsed)
```

---

## 20. Результати виконання програми (Screenshot execution)
```text
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | =================================================================
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | ЛАБОРАТОРНА РОБОТА №5: ОБРОБКА ПОМИЛОК, ФАЙЛИ ТА СЕРІАЛІЗАЦІЯ
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Варіант 9: Імпорт та експорт спортивних результатів
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Конфігурацію успішно завантажено з: config.yaml
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | Режим обробки: Tolerant (skip_invalid=True)
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | =================================================================
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.utils | Початок операції: Sports Data Pipeline Processing
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 5: Ім'я спортсмена не може бути порожнім (рядок 5, поле 'athlete', значення='')
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 10: Результат 3.8 виходить за межі допустимого діапазону [1.0, 2.5] для виду спорту 'Стрибки у висоту' (рядок 10, поле 'result', значення='3.8')
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 11: Вид спорту 'Стрибки з жердиною' не входить до переліку дозволених (рядок 11, поле 'sport', значення='Стрибки з жердиною')
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 12: Результат має бути дійсним числовим значенням: invalid_num (рядок 12, поле 'result', значення='invalid_num')
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 13: Вид спорту 'Велоспорт' не входить до переліку дозволених (рядок 13, поле 'sport', значення='Велоспорт')
2026-10-18 19:07:20 | WARNING | reliable_sports_importer.services | Некоректний запис на рядку 14: Часова мітка 2020-01-01 12:00:00 є старішою за мінімально дозволену 2024-01-01 00:00:00 (рядок 14, поле 'timestamp', значення='2020-01-01T12:00:00')
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.services | Звіт про некоректні записи експортовано у output\error_report.json та output\error_report.csv
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.utils | Операція 'Sports Data Pipeline Processing' успішно завершена за 0.004240 с
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | -----------------------------------------------------------------
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | ПІДСУМКОВА СТАТИСТИКА ВИКОНАННЯ:
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main |   Всього прочитано записів: 14
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main |   Валідних записів (успішно): 8
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main |   Некоректних записів (помилки): 6
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main |   Експортовано у output\sports_results.json: 8
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main |   Окремий звіт про помилки записано у: output\error_report.json
2026-10-18 19:07:20 | INFO    | reliable_sports_importer.main | -----------------------------------------------------------------
```

---

## 21. Результати Експерименту 1 (Strict vs Tolerant)
Вхідний набір: 1000 валідних та 10 невалідних записів.

| Параметр | Strict Mode (`skip_invalid: false`) | Tolerant Mode (`skip_invalid: true`) |
| :--- | :--- | :--- |
| **Оброблено записів** | 1001 (зупинено на 1-му некоректному) | 1010 (повний набір) |
| **Valid** | 1000 | 1000 |
| **Invalid** | 1 | 10 |
| **Exported** | 0 (транзакцію скасовано) | 1000 (усі валідні збережено) |
| **Завершення application** | Перервано винятком `DataExportError` | Завершено успішно з кодом `0` |

*Пояснення доцільності:*
- **Strict mode** доцільний для фінансових, банківських або аудійованих транзакцій, де наявність хоча б одного некоректного запису ставить під сумнів цілісність усього пакету даних.
- **Tolerant mode** доцільний для ETL-конвеєрів великих даних, збору телеметрії та аналітики спортивних результатів, де важливо обробити максимальний обсяг коректних даних, зафіксувавши дефектні рядки в окремому журналі розслідувань.

---

## 22. Результати Експерименту 2 (Streaming vs Eager)

| Кількість записів | Eager time (с) | Streaming time (с) | Eager peak RAM (MB) | Streaming peak RAM (MB) |
| :--- | :--- | :--- | :--- | :--- |
| **10 000** | 0.1112 | 0.0804 | 4.92 MB | 0.0656 MB |
| **100 000** | 0.8792 | 0.8077 | 48.94 MB | 0.0653 MB |
| **500 000** | 4.4826 | 4.0566 | 245.17 MB | 0.0653 MB |

*Висновок:*  
При збільшенні обсягу даних споживання пам'яті у версії **Eager** зростає лінійно $O(N)$ (досягаючи 245 МБ при 500 000 записів), що призведе до `MemoryError` на гігабайтних файлах. Натомість версія **Streaming** підтримує стабільне споживання оперативної пам'яті $O(1)$ на рівні ~0.065 МБ незалежно від розміру файлу, генеруючи об'єкти по одному за запитом.

---

## 23. Результати Експерименту 3 (Exception Chaining Traceback)
```text
Traceback (most recent call last):
  File "C:\labs\Lab_05\src\reliable_sports_importer\validators.py", line 47, in parse_and_validate_record
    result_val = float(result_raw)
                 ^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: 'not_a_number'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\labs\Lab_05\tests\experiments_runner.py", line 200, in run_experiment_3
    parse_and_validate_record(bad_row, line_number=42, config=dummy_cfg)
  File "C:\labs\Lab_05\src\reliable_sports_importer\validators.py", line 49, in parse_and_validate_record
    raise RecordValidationError(
reliable_sports_importer.exceptions.RecordValidationError: Результат має бути дійсним числовим значенням: not_a_number (рядок 42, поле 'result', значення='not_a_number')
```
*Пояснення:* Збереження первинного винятку `ValueError` у ланцюжку через `from error` дає розробнику точне розуміння причини відхилення на рівні системних типів мови Python.

---

## 24. Результати Експерименту 4 (Atomic Output Verification)
- Симуляція збою: всередині блоку запису піднято виняток під час формування JSON.
- Стан цільового файлу: робочий файл `output/atomic_test_production.json` не зазнав жодних змін (зберіг початковий вміст).
- Стан тимчасового файлу: файл `output/atomic_test_production.json.tmp` автоматично видалено блоком `except` контекстного менеджера.
- Додаток контрольовано перехопив `DataExportError` без руйнування даних.

---

## 25. Результати Експерименту 5 (Configuration Errors / Fail-fast)

| № | Сценарій тесту | Отримана реакція системи (Fail-fast) |
|---|----------------|--------------------------------------|
| 1 | Відсутній `config.yaml` | `ConfigurationError: Конфігураційний файл не знайдено: config_non_existent.yaml` |
| 2 | Неправильний синтаксис YAML | `ConfigurationError: Синтаксична помилка у YAML конфігурації: while parsing a flow sequence...` |
| 3 | Немає обов'язкової секції `input` | `ConfigurationError: Некоректна структура конфігурації: 'input'` |
| 4 | Некоректний діапазон `min_value > max_value` | `ConfigurationError: Некоректне правило для 'Стрибки': min_value (300.0) > max_value (10.0)` |
| 5 | Вхідний файл відсутній на диску | `ConfigurationError: Вхідний файл для обробки не знайдено: missing_file.csv` |
| 6 | Порожній список `allowed_sports` | `ConfigurationError: Список дозволених видів спорту (allowed_sports) не може бути порожнім` |

---

## 26. Відповіді на всі 70 контрольних запитань

1. **Що таке exception?**  
   Це спеціальний об'єкт у Python, який сигналізує про виникнення нештатної ситуації чи помилки під час виконання програми та перериває звичайний потік інструкцій.
2. **Для чого використовується try?**  
   Для визначення блоку коду, в якому відстежується можливість виникнення виняткових ситуацій.
3. **Для чого except?**  
   Для перехоплення та обробки конкретного типу винятку, що виник у блоці `try`.
4. **Коли виконується else після try?**  
   Тільки тоді, коли блок `try` завершився успішно без виникнення жодного винятку.
5. **Коли виконується finally?**  
   Завжди і гарантовано: як при нормальному завершенні `try`, так і після перехоплення винятку або перед його аварійним прокиданням нагору.
6. **Для чого використовується raise?**  
   Для явного збудження (підняття) екземпляра або класу винятку в коді.
7. **Що означає raise без аргументів?**  
   Повторне збудження (re-raise) поточного активного винятку з блоку `except` вище по стеку викликів зі збереженням оригінального traceback.
8. **Чому не рекомендується except: pass?**  
   Це антипатерн «ковтання помилок», що приховує баги програміста (наприклад `NameError`, `SyntaxError`) і блокує переривання програми користувачем (`KeyboardInterrupt`).
9. **Чому потрібно перехоплювати конкретні exception types?**  
   Щоб обробляти тільки ті помилки, спосіб відновлення після яких відомий поточному блоку, не маскуючи системні чи програмні дефекти.
10. **Що таке exception hierarchy?**  
    Деревоподібна структура успадкування класів винятків, де на вершині стоїть `BaseException`, нижче `Exception`, а далі предметні доменні винятки.
11. **Для чого створювати custom exceptions?**  
    Щоб надати помилкам семантичний зміст предметної області, передавати додаткові метадані (рядок, поле) та селективно їх фільтрувати.
12. **Що таке exception chaining?**  
    Механізм зв'язування винятків, коли один виняток збуджується в результаті іншого зі збереженням зв'язку між ними.
13. **Що означає raise ... from ...?**  
    Синтаксис явного зв'язування винятків (explicit chaining), що записує оригінальну помилку в атрибут `__cause__`.
14. **Яку перевагу дає chaining для debugging?**  
    У діагностичному повідомленні виводиться повний ланцюжок трасування від первинної системної причини до доменного винятку.
15. **Що означає EAFP?**  
    «Easier to Ask for Forgiveness than Permission» — ідіоматичний підхід у Python: виконання операції без попередніх перевірок із перехопленням можливого винятку.
16. **Що означає LBYL?**  
    «Look Before You Leap» — підхід із попередньою перевіркою всіх умов та стану перед виконанням потенційно небезпечної операції.
17. **Що таке fail-fast?**  
    Принцип проектування, за яким система негайно припиняє роботу при виявленні некоректного стану чи невалідних вхідних параметрів.
18. **Де доцільно застосовувати fail-fast?**  
    На старті програми: при читанні файлів конфігурації, перевірці прав доступу, підключенні до баз даних та валідації аргументів командного рядка.
19. **Що таке context manager?**  
    Об'єкт, який керує часом життя ресурсу і гарантує виконання коду ініціалізації при вході та обов'язкового очищення при виході.
20. **Для чого використовується with?**  
    Для безпечного зв'язування виконання блоку коду з методами входу та виходу контекстного менеджера.
21. **Які methods утворюють context manager protocol?**  
    Методи `__enter__()` та `__exit__(exc_type, exc_val, exc_tb)`.
22. **Що робить __enter__()?**  
    Виділяє ресурс, налаштовує контекст та повертає об'єкт, який прив'язується до змінної після `as`.
23. **Що робить __exit__()?**  
    Звільняє або закриває ресурс; якщо він повертає `True`, виняток придушується, якщо `False` — прокидається нагору.
24. **Чи закриває with файл при exception?**  
    Так, метод `__exit__()` викликається інтерпретатором гарантовано, навіть якщо всередині виник критичний виняток.
25. **Для чого contextlib.contextmanager?**  
    Декоратор, що дозволяє створювати контекстні менеджери за допомогою простих функцій-генераторів із оператором `yield`.
26. **Яку роль має yield у generator-based context manager?**  
    Розділяє фазу ініціалізації ресурсу (до `yield`) та фазу гарантованого очищення (після `yield`, у блоці `finally`).
27. **Що таке pathlib.Path?**  
    Сучасний об'єктно-орієнтований клас стандартної бібліотеки для зручної та кросплатформної роботи зі шляхами файлової системи.
28. **Чому pathlib кращий за ручну конкатенацію шляхів?**  
    Він автоматично враховує роздільники операційної системи (`/` або `\`), запобігає багам ручної конкатенації та містить багатий API операцій з файлами.
29. **Для чого задається encoding="utf-8"?**  
    Щоб робота програми з текстовими файлами була детермінованою та не залежала від регіональних налаштувань кодування ОС (наприклад, Windows CP1251).
30. **Що таке CSV?**  
    Comma-Separated Values — текстовий формат зберігання табличних даних, де колонки розділяються комами або іншими символами.
31. **Для чого csv.reader?**  
    Для построкового читання CSV-файлу у вигляді списків рядків `list[str]`.
32. **Для чого csv.DictReader?**  
    Для читання рядків CSV у вигляді словників `dict[str, str]`, де ключами є заголовки стовпців першого рядка.
33. **Чим DictReader зручний для structured data?**  
    Дозволяє звертатися до значень за назвами колонок замість числових індексів, що підвищує читабельність та стійкість до зміни порядку колонок.
34. **Для чого csv.DictWriter?**  
    Для запису словників у CSV-файл відповідно до переданого списку полів `fieldnames`.
35. **Що таке JSON?**  
    JavaScript Object Notation — текстовий формат обміну структурованими даними на основі пар ключ-значення та масивів.
36. **Що таке serialization?**  
    Процес перетворення об'єктів пам'яті програми (об'єкти, списки, словники) у байтовий або текстовий формат для збереження чи передачі мережею.
37. **Що таке deserialization?**  
    Зворотний процес відновлення внутрішніх структур даних або об'єктів програми з файлу чи текстового потоку.
38. **Чим json.dump() відрізняється від json.dumps()?**  
    `json.dump()` записує JSON безпосередньо у відкритий файловий потік, а `json.dumps()` повертає результат у вигляді Python-рядка `str`.
39. **Чим json.load() відрізняється від json.loads()?**  
    `json.load()` читає та парсить JSON із файлового потоку, а `json.loads()` парсить готовий рядок у пам'яті.
40. **Що таке JSONDecodeError?**  
    Підклас `ValueError`, що сигналізує про синтаксичну некоректність структури документа JSON під час десеріалізації.
41. **Для чого використовується YAML?**  
    Людино-орієнтований формат розмітки, оптимізований для складних конфігураційних файлів із підтримкою коментарів та ієрархії.
42. **Чому рекомендується yaml.safe_load()?**  
    Він парсить лише базові структури і блокує виконання довільного коду через спеціальні теги конструкторів Python, захищаючи від атак.
43. **Які типові сценарії використання JSON?**  
    Обмін повідомленнями у REST API, веб-сервісах, клієнт-серверних протоколах та кешах даних.
44. **Які типові сценарії використання YAML?**  
    Файли конфігурації додатків, пайплайни CI/CD (GitHub Actions, GitLab CI), Kubernetes-маніфести, docker-compose.
45. **Що таке configuration file?**  
    Зовнішній файл, що визначає змінні параметри поведінки програми без необхідності модифікувати та перекомпільовувати код.
46. **Чому configuration краще не hard-code у Python?**  
    Це порушує принципи 12-факторного додатку: параметри мають легко адаптуватися під різні середовища (dev, test, prod).
47. **Що потрібно перевіряти у configuration?**  
    Існування файлів, допустимість числових діапазонів, правильність типів даних та несуперечливість залежних параметрів.
48. **Що таке logging?**  
    Процес системного фіксування подій, інформаційних повідомлень, попереджень та помилок під час виконання програми.
49. **Чим logging відрізняється від print()?**  
    `logging` надає рівні важливості, додає мітки часу, ім'я модуля, керує потоками виводу (консоль, файл) та налаштовується декларативно.
50. **Які існують logging levels?**  
    DEBUG, INFO, WARNING, ERROR, CRITICAL.
51. **Для чого logger.info()?**  
    Для фіксування штатних ключових подій нормальної роботи програми (старт конвеєра, завершення імпорту).
52. **Для чого logger.warning()?**  
    Для фіксування некритичних аномалій чи дефектних даних, які не переривають виконання всієї програми (пропуск некоректного рядка).
53. **Для чого logger.error()?**  
    Для фіксування серйозних помилок, через які певна функціональна операція не змогла завершитися.
54. **Для чого logger.exception()?**  
    Записує повідомлення рівня ERROR і автоматично додає до журналу повне трасування стеку викликів (traceback).
55. **Що містить traceback?**  
    Список викликів функцій у зворотному порядку із зазначенням файлів, номерів рядків та коду, що призвів до збою.
56. **Чому secrets не можна записувати в logs?**  
    Журнали часто зберігаються на відкритих дисках, передаються в ELK/Splunk або переглядаються багатьма розробниками, що створює ризик витоку паролів чи токенів.
57. **Що таке streaming I/O?**  
    Метод обробки даних фрагментами (построково чи блоками) без завантаження всього масиву у пам'ять одночасно.
58. **Яка перевага streaming для великих files?**  
    Константне споживання оперативної пам'яті $O(1)$, що запобігає переповненню пам'яті (OutOfMemory).
59. **Що таке eager file loading?**  
    Жадібне завантаження, коли весь файл цілком зчитується в пам'ять (наприклад, через `list(reader)` або `file.read()`).
60. **Чому list(reader) може бути небажаним?**  
    Для багатогігабайтних файлів це призводить до аварійного завершення програми внаслідок вичерпання RAM.
61. **Що таке strict validation mode?**  
    Режим суворої валідації: виявлення першого ж дефектного запису перериває обробку та анулює транзакцію.
62. **Що таке tolerant mode?**  
    Толерантний режим: дефектні записи ігноруються або реєструються в журналі, а валідні дані продовжують оброблятися.
63. **Коли доцільно використовувати strict mode?**  
    У платіжних системах, бухгалтерії, міграції баз даних, де частковий запис неприпустимий.
64. **Коли tolerant mode?**  
    В аналітиці, зборі логів, імпорті спортивних результатів та масових потоках датчиків.
65. **Що таке atomic write?**  
    Операція запису файлу, яка виконується за принципом «все або нічого»: файл або оновлюється повністю, або залишається в первинному стані.
66. **Для чого використовується temporary file?**  
    Дані спочатку записуються у тимчасовий файл `*.tmp`, і лише після успішної верифікації файл замінює цільовий.
67. **Що може статися при звичайному output write та аварійному завершенні?**  
    Вихідний файл буде пошкоджено або обрізано (наприклад, незакритий JSON масив), а попередні дані буде назавжди втрачено.
68. **Навіщо видаляти temporary file після error?**  
    Щоб не засмічувати файлову систему сміттєвими тимчасовими файлами.
69. **Що таке JSON Lines?**  
    Текстовий формат (JSONL), де кожен окремий рядок є повноцінним незалежним валідним JSON-об'єктом.
70. **Чому JSON Lines зручний для streaming?**  
    Він дозволяє читати та дописувати об'єкти построково без парсингу гігантських списків із квадратними дужками.

---

## 27. Висновок
Під час виконання лабораторної роботи №5 було повністю опановано сучасні стандарти розробки надійних Python-додатків:
1. **Обробка помилок:** створено власну ієрархію винятків на базі `ApplicationError`, реалізовано зв'язування винятків через `from error` для збереження першопричини та усунуто антипатерн «ковтання помилок».
2. **Конфігурація (Fail-fast):** винесено бізнес-правила (діапазони результатів для кожного виду спорту, категорії, шляхи) у зовнішній `config.yaml`, семантика якого валідується на етапі запуску.
3. **Потоковий I/O:** впроваджено генератори для побудови конвеєра імпорту та експорту, що дозволило зберегти стабільне споживання пам'яті $O(1)$ (~0.065 МБ) навіть на 500 000 записах.
4. **Атомарність експорту:** завдяки розробленому контекстному менеджеру `atomic_file_writer` гарантовано збереження цілісності результуючих файлів у разі збоїв та винятків під час запису.
5. **Тестування:** проект повністю покрито юніт-тестами, успішно пройдено верифікацію статичного типізатора `mypy` без жодних зауважень.
