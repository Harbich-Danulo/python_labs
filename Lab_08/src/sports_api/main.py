"""Точка входу запуску FastAPI REST API та демонстрації асинхронного клієнта."""

import asyncio
import os
import sys
import uvicorn
from sqlalchemy.orm import Session
from sports_api.database import SessionLocal, init_db
from sports_api.external_api import fetch_many_rankings_concurrent
from sports_api.models import Athlete, Result, Sport
from sports_api.services import SportsService


def seed_initial_data() -> None:
    """Заповнює базу даних еталонними тестовими записами при першому запуску."""
    init_db()
    session: Session = SessionLocal()
    try:
        service = SportsService(session)
        if not service.list_sports():
            print("Ініціалізація початкових даних для предметної області...")
            s1 = service.register_sport("Біг на 100м", "сек", is_lower_better=True)
            s2 = service.register_sport("Плавання 50м", "сек", is_lower_better=True)
            s3 = service.register_sport("Стрибки у довжину", "м", is_lower_better=False)

            a1 = service.register_athlete("Данило Гарбіч", "Україна", 21)
            a2 = service.register_athlete("Олександр Зінченко", "Україна", 27)
            a3 = service.register_athlete("Ярослава Магучіх", "Україна", 22)
            a4 = service.register_athlete("Михайло Романчук", "Україна", 28)

            service.record_result(a1.id, s1.id, 10.35, "Фінал", "Меморіал")
            service.record_result(a2.id, s1.id, 11.20, "Дорослі", "Кубок НОК")
            service.record_result(a4.id, s2.id, 21.80, "Дорослі", "Олімпійський відбір")
            service.record_result(a1.id, s2.id, 24.15, "Юніори", "Кубок ректора")
            service.record_result(a3.id, s3.id, 8.12, "Дорослі", "Diamond League")
            service.record_result(a1.id, s3.id, 7.85, "Дорослі", "Універсіада")
            print("Еталонні дані завантажено успішно!")
    finally:
        session.close()


def run_server() -> None:
    """Запускає веб-сервер Uvicorn з додатком FastAPI."""
    seed_initial_data()
    print("=" * 70)
    print(" Запуск FastAPI сервера: http://127.0.0.1:8000")
    print(" Інтерактивна документація Swagger UI: http://127.0.0.1:8000/docs")
    print(" Альтернативна документація ReDoc: http://127.0.0.1:8000/redoc")
    print("=" * 70)
    uvicorn.run("sports_api.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run_server()
