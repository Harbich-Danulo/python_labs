# Data Processor (Лабораторна робота №2)

Навчальний проєкт з дисципліни **«Професійний Python»** (Лабораторна робота №2).  
**Тема:** «Структури даних та функціональна декомпозиція».  
**Варіант №9:** «Облік спортивних результатів».

## Опис проєкту

Проєкт демонструє професійне використання базових та спеціалізованих структур даних мови Python (`list`, `tuple`, `set`, `dict`, `collections.Counter`, `collections.defaultdict`, `collections.deque`), спискових включень (`comprehensions`), генераторних виразів, функціональної декомпозиції, замикань (`closures`), функцій вищого порядку, функцій зі змінною кількістю аргументів (`*args`, `**kwargs`) та параметризованих декораторів (`decorators`).

Також реалізовано експериментальну частину з вимірюванням часу та оцінюванням алгоритмічної складності операцій (Big-O notation).

---

## Структура проєкту

```text
lab2/
├── .gitignore
├── pyproject.toml
├── README.md
├── REPORT.md
├── report.html
├── report.pdf
├── Звіт_Лабораторна_2_Гарбіч.pdf
│
├── src/
│   └── data_processor/
│       ├── __init__.py
│       ├── data.py          # Базові набори даних (list of dicts, tuples, sets)
│       ├── decorators.py    # Декоратори (@measure_time, @repeat, deque history)
│       ├── processors.py    # Фільтрація, індексація, групування, Counter
│       ├── analytics.py     # Агрегація, сортування, closures, *args, **kwargs, pipeline
│       └── main.py          # Точка входу, демонстрація та бенчмарк
│
└── tests/
    └── test_data_processor.py # Автоматизовані модульні тести
```

---

## Встановлення та запуск

1. Створення віртуального середовища:
   ```bash
   python -m venv .venv
   ```

2. Активація середовища:
   - **Windows**: `.venv\Scripts\activate`
   - **Linux / macOS**: `source .venv/bin/activate`

3. Встановлення у режимі редагування:
   ```bash
   python -m pip install -e .
   ```

4. Запуск програми:
   ```bash
   python -m data_processor.main
   # або
   data-processor
   ```

5. Запуск тестів:
   ```bash
   python tests/test_data_processor.py
   ```

---

## Автор

- **Студент:** Гарбіч Данило
- **Група:** ФЕП-31с
- **Факультет:** Факультет електроніки та комп'ютерних технологій
- **Університет:** Львівський національний університет імені Івана Франка
- **Рік:** 2026
