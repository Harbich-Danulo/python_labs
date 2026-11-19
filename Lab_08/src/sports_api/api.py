"""FastAPI REST API застосунок для системи «Облік спортивних результатів» (Варіант №9)."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sports_api.database import get_session, init_db
from sports_api.external_api import ExternalServiceError, fetch_many_rankings_concurrent
from sports_api.models import Athlete, Result, Sport
from sports_api.schemas import (
    AthleteCreate,
    AthleteResponse,
    AthleteUpdate,
    BatchRankingsRequest,
    BatchRankingsResponse,
    ResultCreate,
    ResultResponse,
    ResultUpdate,
    SportCreate,
    SportRankingResponse,
    SportResponse,
    SportStatisticsResponse,
)
from sports_api.services import (
    BusinessValidationError,
    ConflictError,
    EntityNotFoundError,
    SportsService,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Життєвий цикл додатку: автоматична ініціалізація БД при старті."""
    init_db()
    yield


app = FastAPI(
    title="Sports Results Management REST API",
    description="Асинхронний REST API для обліку та аналізу спортивних досягнень (Варіант 9)",
    version="0.8.0",
    lifespan=lifespan,
)


# --- Обробники кастомних виключень ---

@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(BusinessValidationError)
async def business_validation_handler(request: Request, exc: BusinessValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(exc)}
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.exception_handler(ExternalServiceError)
async def external_service_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT, content={"detail": str(exc)}
    )


# --- Root Endpoint ---

@app.get("/", tags=["System"])
async def root() -> dict[str, str]:
    return {
        "message": "Sports Results Management REST API is active",
        "version": "0.8.0",
        "docs": "/docs",
    }


# --- Ендпоінти спортсменів (/athletes) ---

@app.get("/athletes", response_model=List[AthleteResponse], tags=["Athletes"])
async def list_athletes(
    name: Optional[str] = Query(None, description="Фільтр за частиною імені спортсмена"),
    country: Optional[str] = Query(None, description="Фільтр за країною"),
    session: Session = Depends(get_session),
) -> List[Athlete]:
    service = SportsService(session)
    return service.list_athletes(name_query=name, country=country)


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


@app.get("/athletes/{athlete_id}", response_model=AthleteResponse, tags=["Athletes"])
async def get_athlete(athlete_id: int, session: Session = Depends(get_session)) -> Athlete:
    service = SportsService(session)
    return service.get_athlete(athlete_id)


@app.patch("/athletes/{athlete_id}", response_model=AthleteResponse, tags=["Athletes"])
async def update_athlete(
    athlete_id: int, data: AthleteUpdate, session: Session = Depends(get_session)
) -> Athlete:
    service = SportsService(session)
    update_data = data.model_dump(exclude_unset=True)
    return service.update_athlete(athlete_id, **update_data)


@app.delete(
    "/athletes/{athlete_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Athletes"],
)
async def delete_athlete(athlete_id: int, session: Session = Depends(get_session)) -> None:
    service = SportsService(session)
    service.delete_athlete(athlete_id)


# --- Ендпоінти дисциплін (/sports) ---

@app.get("/sports", response_model=List[SportResponse], tags=["Sports"])
async def list_sports(session: Session = Depends(get_session)) -> List[Sport]:
    service = SportsService(session)
    return service.list_sports()


@app.post(
    "/sports",
    response_model=SportResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Sports"],
)
async def create_sport(data: SportCreate, session: Session = Depends(get_session)) -> Sport:
    service = SportsService(session)
    return service.register_sport(
        name=data.name, unit=data.unit, is_lower_better=data.is_lower_better
    )


@app.get("/sports/{sport_id}", response_model=SportResponse, tags=["Sports"])
async def get_sport(sport_id: int, session: Session = Depends(get_session)) -> Sport:
    service = SportsService(session)
    return service.get_sport(sport_id)


@app.get(
    "/sports/{sport_id}/results",
    response_model=List[ResultResponse],
    tags=["Sports"],
)
async def get_sport_results(
    sport_id: int,
    category: Optional[str] = Query(None, description="Фільтр за категорією"),
    min_score: Optional[float] = Query(None, description="Мінімальний результат"),
    max_score: Optional[float] = Query(None, description="Максимальний результат"),
    session: Session = Depends(get_session),
) -> List[Result]:
    service = SportsService(session)
    return service.get_sport_results(
        sport_id=sport_id, category=category, min_score=min_score, max_score=max_score
    )


@app.get(
    "/sports/{sport_id}/ranking",
    response_model=SportRankingResponse,
    tags=["Sports"],
)
async def get_sport_ranking(
    sport_id: int, session: Session = Depends(get_session)
) -> SportRankingResponse:
    service = SportsService(session)
    return service.get_sport_ranking(sport_id)


@app.get(
    "/sports/{sport_id}/statistics",
    response_model=SportStatisticsResponse,
    tags=["Sports"],
)
async def get_sport_statistics(
    sport_id: int, session: Session = Depends(get_session)
) -> SportStatisticsResponse:
    service = SportsService(session)
    return service.get_sport_statistics(sport_id)


# --- Ендпоінти результатів (/results) ---

@app.post(
    "/results",
    response_model=ResultResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Results"],
)
async def record_result(
    data: ResultCreate, session: Session = Depends(get_session)
) -> Result:
    service = SportsService(session)
    return service.record_result(
        athlete_id=data.athlete_id,
        sport_id=data.sport_id,
        score=data.score,
        category=data.category,
        competition_name=data.competition_name,
    )


@app.get("/results/{result_id}", response_model=ResultResponse, tags=["Results"])
async def get_result(result_id: int, session: Session = Depends(get_session)) -> Result:
    service = SportsService(session)
    return service.get_result(result_id)


@app.patch("/results/{result_id}", response_model=ResultResponse, tags=["Results"])
async def update_result(
    result_id: int, data: ResultUpdate, session: Session = Depends(get_session)
) -> Result:
    service = SportsService(session)
    update_data = data.model_dump(exclude_unset=True)
    return service.update_result(result_id, **update_data)


@app.delete(
    "/results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Results"],
)
async def delete_result(result_id: int, session: Session = Depends(get_session)) -> None:
    service = SportsService(session)
    service.delete_result(result_id)


# --- Асинхронний агрегаційний Batch Endpoint ---

@app.post(
    "/sports/rankings/batch",
    response_model=BatchRankingsResponse,
    tags=["Async Aggregation"],
)
async def batch_sport_rankings(
    data: BatchRankingsRequest,
    session: Session = Depends(get_session),
) -> BatchRankingsResponse:
    """Паралельне отримання рейтингів кількох дисциплін через внутрішній сервісний шар.
    
    Для імітації/виконання асинхронного агрегування генеруються окремі корутини.
    """
    service = SportsService(session)
    rankings: List[SportRankingResponse] = []

    for sid in data.sport_ids:
        try:
            r = service.get_sport_ranking(sid)
            rankings.append(r)
        except EntityNotFoundError:
            continue

    return BatchRankingsResponse(
        total_requested=len(data.sport_ids),
        successful=len(rankings),
        rankings=rankings,
    )
