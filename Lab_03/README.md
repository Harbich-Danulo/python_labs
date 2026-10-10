# Stream Processor (Лабораторна робота №3)

Навчальний проєкт з дисципліни **«Професійний Python»** (Лабораторна робота №3).  
**Тема:** «Ітератори, генератори та потокова обробка даних».  
**Варіант №9:** «Потокова обробка спортивних результатів».

## Опис проєкту

Проєкт реалізує потоковий конвеєр (`streaming lazy pipeline`) для обробки великих масивів спортивних результатів без повного завантаження файлу в оперативну пам'ять (з використанням `yield`, `yield from`, `generator expressions`, протоколу `__iter__` / `__next__`, та модуля `itertools`).

### Основні можливості:
- **Streaming CSV reader & validation**: потокове читання та очищення рядків файлу через генератори.
- **Lazy pipeline**: конвеєр стадій `read -> clean -> parse -> validate -> filter -> transform -> aggregate`.
- **itertools modules**: використання `islice` для обмеження вибірки, `pairwise` для аналізу дельт результатів, `chain` для об'єднання потоків даних.
- **Batching**: пакетна обробка потоку через `islice`.
- **Eager vs Lazy Benchmarking**: експериментальне порівняння часу виконання, використання пам'яті (`peak memory`) та часу отримання першого результату (`time-to-first-result`) на вибірках **10 000**, **100 000** та **500 000** записів.

---

## Структура проєкту

```text
lab3/
├── .gitignore
├── pyproject.toml
├── README.md
├── REPORT.md
├── report.html
├── report.pdf
├── Звіт_Лабораторна_3_Гарбіч.pdf
├── data/
│   └── input.csv                  # Зразок вхідних даних зі спортивними результатами
├── src/
│   └── stream_processor/
│       ├── __init__.py
│       ├── models.py              # NamedTuple SportsRecord, класи SportsRange/Iterator
│       ├── readers.py             # Читання та очищення потоку (yield from)
│       ├── parsers.py             # Парсер CSV рядків у словники
│       ├── filters.py             # Потокова валідація та лінива фільтрація
│       ├── transformations.py     # Нормалізація полів та пакетування (batching)
│       ├── analytics.py           # Потокові агрегації (avg, min/max, pairwise)
│       ├── pipeline.py            # Збирання лінивого конвеєра
│       └── main.py                # Демонстрація та бенчмарк (Eager vs Lazy)
└── tests/
    └── test_stream_processor.py   # Модульні тести компонентів конвеєра
```

---

## Встановлення та запуск

1. Створення віртуального середовища:
   ```bash
   python -m venv .venv
   ```

2. Активація:
   - **Windows**: `.venv\Scripts\activate`
   - **Linux / macOS**: `source .venv/bin/activate`

3. Встановлення у режимі редагування:
   ```bash
   python -m pip install -e .
   ```

4. Запуск програми:
   ```bash
   python -m stream_processor.main
   # або
   stream-processor
   ```

5. Запуск тестів:
   ```bash
   python tests/test_stream_processor.py
   ```

---

## Автор

- **Студент:** Гарбіч Данило
- **Група:** ФЕП-31с
- **Факультет:** Факультет електроніки та комп'ютерних технологій
- **Університет:** Львівський національний університет імені Івана Франка
- **Рік:** 2026
