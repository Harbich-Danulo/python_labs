"""Пряма взаємодія з базою даних SQLite через стандартний інтерфейс Python DB-API (модуль sqlite3).

Демонструє виконання параметризованих запитів (parameterized queries) для захисту від SQL-ін'єкцій,
а також агрегатні SQL-функції (AVG, MAX, MIN, COUNT, GROUP BY).
"""

import sqlite3
from typing import Any, Dict, List, Optional, Tuple


def get_sqlite_connection(db_path: str) -> sqlite3.Connection:
    """Створює підключення до SQLite з увімкненими foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def find_results_by_sport_dbapi(db_path: str, sport_name: str) -> List[Dict[str, Any]]:
    """Пошук усіх результатів для заданого виду спорту через DB-API з параметризованим запитом."""
    query = """
        SELECT 
            r.id,
            a.name AS athlete_name,
            s.name AS sport_name,
            r.score,
            s.unit,
            r.category,
            r.competition_name
        FROM results r
        JOIN athletes a ON r.athlete_id = a.id
        JOIN sports s ON r.sport_id = s.id
        WHERE s.name = ?
        ORDER BY r.score ASC;
    """
    conn = get_sqlite_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, (sport_name,))
        rows = cursor.fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            results.append({
                "id": row[0],
                "athlete_name": row[1],
                "sport_name": row[2],
                "score": row[3],
                "unit": row[4],
                "category": row[5],
                "competition_name": row[6],
            })
        return results
    finally:
        conn.close()


def get_sport_statistics_dbapi(db_path: str, sport_name: str) -> Optional[Dict[str, Any]]:
    """Обчислення агрегатних статистичних показників (COUNT, AVG, MIN, MAX) через SQL DB-API."""
    query = """
        SELECT 
            s.name,
            s.unit,
            COUNT(r.id) AS total_results,
            AVG(r.score) AS avg_score,
            MIN(r.score) AS min_score,
            MAX(r.score) AS max_score
        FROM sports s
        LEFT JOIN results r ON s.id = r.sport_id
        WHERE s.name = ?
        GROUP BY s.id, s.name, s.unit;
    """
    conn = get_sqlite_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, (sport_name,))
        row = cursor.fetchone()
        if not row or row[2] == 0:
            return None
        return {
            "sport_name": row[0],
            "unit": row[1],
            "total_results": row[2],
            "avg_score": round(float(row[3]), 2) if row[3] is not None else 0.0,
            "min_score": float(row[4]) if row[4] is not None else 0.0,
            "max_score": float(row[5]) if row[5] is not None else 0.0,
        }
    finally:
        conn.close()


def execute_parameterized_query(
    db_path: str, sql: str, params: Tuple[Any, ...] = ()
) -> List[Tuple[Any, ...]]:
    """Універсальне безпечне виконання параметризованого SQL-запиту з поверненням рядків."""
    conn = get_sqlite_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()
