"""Асинхронний мережевий модуль: взаємодія через HTTPX, паралельні Task/gather, Semaphore, timeout та retry."""

import asyncio
from typing import Any, Dict, List, Optional
import httpx


class ExternalServiceError(Exception):
    """Помилка виклику зовнішнього HTTP-сервісу."""
    pass


async def fetch_sport_ranking(
    client: httpx.AsyncClient, base_url: str, sport_id: int
) -> Dict[str, Any]:
    """Виконує одиничний асинхронний HTTP GET запит рейтингу дисципліни."""
    url = f"{base_url.rstrip('/')}/sports/{sport_id}/ranking"
    response = await client.get(url)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    return data


async def fetch_ranking_with_retry(
    client: httpx.AsyncClient,
    base_url: str,
    sport_id: int,
    semaphore: asyncio.Semaphore,
    attempts: int = 3,
    backoff_factor: float = 0.5,
) -> Dict[str, Any]:
    """Отримує рейтинг спорту через Semaphore із повторними спробами (retry) та експоненційною затримкою."""
    async with semaphore:
        for attempt in range(1, attempts + 1):
            try:
                return await fetch_sport_ranking(client, base_url, sport_id)
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                if attempt == attempts:
                    raise ExternalServiceError(
                        f"Вичерпано спроби ({attempts}) запиту рейтингу sport_id={sport_id}: {exc}"
                    ) from exc
                await asyncio.sleep(attempt * backoff_factor)
        raise ExternalServiceError("Непередбачуваний стан циклу retry.")


async def fetch_many_rankings_concurrent(
    base_url: str,
    sport_ids: List[int],
    max_concurrency: int = 3,
    timeout: float = 5.0,
    attempts: int = 3,
    client: Optional[httpx.AsyncClient] = None,
) -> List[Dict[str, Any]]:
    """Паралельно отримує рейтинги кількох дисциплін через Task і gather, обмежуючи паралелізм Semaphore."""
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _execute_with_client(c: httpx.AsyncClient) -> List[Dict[str, Any]]:
        # Створюємо список асинхронних завдань (asyncio.Task)
        tasks: List[asyncio.Task[Dict[str, Any]]] = [
            asyncio.create_task(
                fetch_ranking_with_retry(
                    client=c,
                    base_url=base_url,
                    sport_id=sid,
                    semaphore=semaphore,
                    attempts=attempts,
                )
            )
            for sid in sport_ids
        ]

        # Паралельне виконання через asyncio.gather із загальним timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=False),
                timeout=timeout,
            )
            return list(results)
        except asyncio.TimeoutError as exc:
            # Скасовуємо незавершені таски при таймауті
            for t in tasks:
                if not t.done():
                    t.cancel()
            raise ExternalServiceError(
                f"Операція паралельного отримання рейтингів перевищила ліміт часу {timeout} с."
            ) from exc

    if client is not None:
        return await _execute_with_client(client)
    else:
        async with httpx.AsyncClient(timeout=timeout) as new_client:
            return await _execute_with_client(new_client)
