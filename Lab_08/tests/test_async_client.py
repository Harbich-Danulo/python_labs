"""Асинхронні тести для модуля external_api (HTTPX, asyncio.Task, gather, Semaphore, timeout, retry)."""

import asyncio
from typing import Any
import pytest
from httpx import AsyncClient
from sports_api.external_api import (
    ExternalServiceError,
    fetch_many_rankings_concurrent,
    fetch_ranking_with_retry,
    fetch_sport_ranking,
)


@pytest.mark.asyncio
async def test_async_root_endpoint(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "0.8.0"


@pytest.mark.asyncio
async def test_fetch_sport_ranking(async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
    sport_id = seed_data["sports"][0].id
    ranking = await fetch_sport_ranking(async_client, "http://test", sport_id)
    assert ranking["sport_id"] == sport_id
    assert ranking["sport_name"] == "Біг на 100м"
    assert len(ranking["ranking"]) == 2


@pytest.mark.asyncio
async def test_fetch_ranking_with_retry(async_client: AsyncClient, seed_data: dict[str, Any]) -> None:
    sport_id = seed_data["sports"][0].id
    semaphore = asyncio.Semaphore(2)
    ranking = await fetch_ranking_with_retry(
        client=async_client,
        base_url="http://test",
        sport_id=sport_id,
        semaphore=semaphore,
        attempts=2,
        backoff_factor=0.01,
    )
    assert ranking["sport_id"] == sport_id


@pytest.mark.asyncio
async def test_fetch_many_rankings_concurrent(
    async_client: AsyncClient, seed_data: dict[str, Any]
) -> None:
    s1_id = seed_data["sports"][0].id
    s2_id = seed_data["sports"][1].id

    # Виконуємо паралельний запит двох рейтингів через Task/gather/Semaphore
    rankings = await fetch_many_rankings_concurrent(
        base_url="http://test",
        sport_ids=[s1_id, s2_id],
        max_concurrency=2,
        timeout=3.0,
        attempts=2,
        client=async_client,
    )
    assert len(rankings) == 2
    names = [r["sport_name"] for r in rankings]
    assert "Біг на 100м" in names
    assert "Стрибки у довжину" in names


@pytest.mark.asyncio
async def test_fetch_many_rankings_timeout(
    async_client: AsyncClient, seed_data: dict[str, Any]
) -> None:
    s1_id = seed_data["sports"][0].id

    # Штучний наднизький таймаут для перевірки збудження ExternalServiceError
    with pytest.raises(ExternalServiceError, match="перевищила ліміт часу"):
        await fetch_many_rankings_concurrent(
            base_url="http://test",
            sport_ids=[s1_id],
            max_concurrency=1,
            timeout=0.000001,
            client=async_client,
        )


@pytest.mark.asyncio
async def test_retry_exhaustion_on_404(async_client: AsyncClient) -> None:
    semaphore = asyncio.Semaphore(1)
    with pytest.raises(ExternalServiceError, match="Вичерпано спроби"):
        await fetch_ranking_with_retry(
            client=async_client,
            base_url="http://test",
            sport_id=9999,
            semaphore=semaphore,
            attempts=2,
            backoff_factor=0.01,
        )
