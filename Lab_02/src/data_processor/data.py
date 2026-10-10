"""Data module storing athletes records and sports categories."""

from typing import Any

# Default structured dataset using list of dicts, tuples and sets
athletes: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Ярослава Магучіх",
        "sport": "Стрибки у висоту",
        "result": 2.10,
        "category": "Дорослі",
        "meta": ("WR", "Україна", 2024),  # tuple
    },
    {
        "id": 2,
        "name": "Ірина Геращенко",
        "sport": "Стрибки у висоту",
        "result": 2.00,
        "category": "Дорослі",
        "meta": ("PB", "Україна", 2023),
    },
    {
        "id": 3,
        "name": "Юлія Левченко",
        "sport": "Стрибки у висоту",
        "result": 1.95,
        "category": "Дорослі",
        "meta": ("SB", "Україна", 2022),
    },
    {
        "id": 4,
        "name": "Олег Верняєв",
        "sport": "Спортивна гімнастика",
        "result": 15.30,
        "category": "Майстри",
        "meta": ("OG", "Україна", 2016),
    },
    {
        "id": 5,
        "name": "Ілля Ковтун",
        "sport": "Спортивна гімнастика",
        "result": 15.65,
        "category": "Юніори",
        "meta": ("ECH", "Україна", 2024),
    },
    {
        "id": 6,
        "name": "Михайло Романчук",
        "sport": "Плавання",
        "result": 880.20,
        "category": "Дорослі",
        "meta": ("NR", "Україна", 2021),
    },
    {
        "id": 7,
        "name": "Олександр Желтяков",
        "sport": "Плавання",
        "result": 895.10,
        "category": "Юніори",
        "meta": ("WJC", "Україна", 2023),
    },
    {
        "id": 8,
        "name": "Марина Бех-Романчук",
        "sport": "Стрибки у довжину",
        "result": 6.93,
        "category": "Дорослі",
        "meta": ("PB", "Україна", 2022),
    },
]

# Set of all officially registered categories
all_categories: set[str] = {"Дорослі", "Юніори", "Майстри"}
