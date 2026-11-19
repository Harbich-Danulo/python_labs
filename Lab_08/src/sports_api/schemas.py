"""Pydantic-схеми для валідації запитів, відповідей та документації OpenAPI/Swagger."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Схеми для спорту (Sport) ---

class SportBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Назва дисципліни")
    unit: str = Field(..., min_length=1, max_length=50, description="Одиниця вимірювання (сек, м тощо)")
    is_lower_better: bool = Field(False, description="True, якщо менший результат є кращим (біг, плавання)")


class SportCreate(SportBase):
    pass


class SportResponse(SportBase):
    id: int = Field(..., description="Унікальний ідентифікатор виду спорту")

    model_config = ConfigDict(from_attributes=True)


# --- Схеми для спортсмена (Athlete) ---

class AthleteBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Повне ім'я спортсмена")
    country: str = Field("Україна", min_length=2, max_length=100, description="Країна або клуб")
    age: int = Field(..., ge=5, le=120, description="Вік спортсмена (від 5 до 120 років)")


class AthleteCreate(AthleteBase):
    pass


class AthleteUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150, description="Нове ім'я спортсмена")
    country: Optional[str] = Field(None, min_length=2, max_length=100, description="Нова країна")
    age: Optional[int] = Field(None, ge=5, le=120, description="Новий вік")


class AthleteResponse(AthleteBase):
    id: int = Field(..., description="Унікальний ідентифікатор спортсмена")

    model_config = ConfigDict(from_attributes=True)


# --- Схеми для результатів (Result) ---

class ResultBase(BaseModel):
    athlete_id: int = Field(..., gt=0, description="ID спортсмена")
    sport_id: int = Field(..., gt=0, description="ID виду спорту")
    score: float = Field(..., gt=0.0, description="Числовий показник результату (повинен бути більше 0)")
    category: str = Field(..., min_length=2, max_length=50, description="Категорія (Юніори, Дорослі тощо)")
    competition_name: Optional[str] = Field(None, max_length=200, description="Назва турніру/змагань")


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseModel):
    score: Optional[float] = Field(None, gt=0.0, description="Оновлений результат")
    category: Optional[str] = Field(None, min_length=2, max_length=50, description="Оновлена категорія")
    competition_name: Optional[str] = Field(None, max_length=200, description="Оновлена назва турніру")


class ResultResponse(ResultBase):
    id: int = Field(..., description="Унікальний ідентифікатор результату")
    created_at: datetime = Field(..., description="Дата та час фіксації виступу")

    model_config = ConfigDict(from_attributes=True)


class ResultDetailResponse(ResultResponse):
    athlete_name: str = Field(..., description="Ім'я спортсмена")
    sport_name: str = Field(..., description="Назва виду спорту")
    unit: str = Field(..., description="Одиниця вимірювання")


# --- Схеми аналітики та рейтингів ---

class RankedAthleteItem(BaseModel):
    rank: int = Field(..., description="Місце в турнірній таблиці")
    athlete_id: int = Field(..., description="ID спортсмена")
    athlete_name: str = Field(..., description="Ім'я спортсмена")
    country: str = Field(..., description="Країна атлета")
    score: float = Field(..., description="Результат")
    category: str = Field(..., description="Категорія")
    competition: str = Field(..., description="Змагання")


class SportRankingResponse(BaseModel):
    sport_id: int = Field(..., description="ID дисципліни")
    sport_name: str = Field(..., description="Назва виду спорту")
    unit: str = Field(..., description="Одиниця вимірювання")
    is_lower_better: bool = Field(..., description="Критерій першості")
    total_results: int = Field(..., description="Кількість зафіксованих результатів")
    best_score: Optional[float] = Field(None, description="Найкращий результат у дисципліні")
    average_score: float = Field(..., description="Середній результат учасників")
    ranking: List[RankedAthleteItem] = Field(..., description="Відсортована турнірна таблиця")


class SportStatisticsResponse(BaseModel):
    sport_id: int = Field(..., description="ID виду спорту")
    sport_name: str = Field(..., description="Назва виду спорту")
    unit: str = Field(..., description="Одиниця вимірювання")
    total_results: int = Field(..., description="Кількість залікових виступів")
    avg_score: float = Field(..., description="Середній бал")
    min_score: float = Field(..., description="Мінімальний показник")
    max_score: float = Field(..., description="Максимальний показник")


# --- Схеми пакетних (Batch) асинхронних операцій ---

class BatchRankingsRequest(BaseModel):
    sport_ids: List[int] = Field(
        ..., min_length=1, max_length=20, description="Список ID видів спорту для отримання рейтингів"
    )


class BatchRankingsResponse(BaseModel):
    total_requested: int = Field(..., description="Кількість запитаних дисциплін")
    successful: int = Field(..., description="Кількість успішно отриманих рейтингів")
    rankings: List[SportRankingResponse] = Field(..., description="Список отриманих рейтингів")
