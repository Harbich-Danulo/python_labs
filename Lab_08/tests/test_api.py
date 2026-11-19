"""Синхронні тести ендпоінтів REST API (FastAPI TestClient)."""

from typing import Any
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["message"] == "Sports Results Management REST API is active"


def test_create_and_get_sport(client: TestClient) -> None:
    # 1. POST /sports
    res = client.post("/sports", json={"name": "Біг на 200м", "unit": "сек", "is_lower_better": True})
    assert res.status_code == 201
    sport_data = res.json()
    assert sport_data["id"] is not None
    assert sport_data["name"] == "Біг на 200м"
    sport_id = sport_data["id"]

    # 2. GET /sports/{id}
    res_get = client.get(f"/sports/{sport_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == sport_id

    # 3. GET /sports list
    res_list = client.get("/sports")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. Duplicate name -> 409 Conflict
    res_dup = client.post("/sports", json={"name": "Біг на 200м", "unit": "сек", "is_lower_better": True})
    assert res_dup.status_code == 409


def test_athlete_endpoints(client: TestClient) -> None:
    # 1. POST /athletes
    res = client.post("/athletes", json={"name": "Данило Гарбіч", "country": "Україна", "age": 21})
    assert res.status_code == 201
    athlete = res.json()
    a_id = athlete["id"]

    # 2. Validation error (age too low) -> 422
    res_val = client.post("/athletes", json={"name": "Тест", "country": "Україна", "age": 3})
    assert res_val.status_code == 422

    # 3. GET /athletes with query params
    res_search = client.get("/athletes", params={"name": "Гарбіч", "country": "Україна"})
    assert res_search.status_code == 200
    assert len(res_search.json()) == 1

    # 4. PATCH /athletes/{id}
    res_patch = client.patch(f"/athletes/{a_id}", json={"age": 22})
    assert res_patch.status_code == 200
    assert res_patch.json()["age"] == 22

    # 5. GET /athletes/{id}
    res_get = client.get(f"/athletes/{a_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Данило Гарбіч"

    # 6. DELETE /athletes/{id} -> 204
    res_del = client.delete(f"/athletes/{a_id}")
    assert res_del.status_code == 204

    # 7. GET after delete -> 404
    assert client.get(f"/athletes/{a_id}").status_code == 404


def test_results_endpoints(client: TestClient, seed_data: dict[str, Any]) -> None:
    sport_id = seed_data["sports"][0].id
    athlete_id = seed_data["athletes"][0].id

    # 1. POST /results
    payload = {
        "athlete_id": athlete_id,
        "sport_id": sport_id,
        "score": 10.25,
        "category": "Фінал",
        "competition_name": "Олімпіада",
    }
    res = client.post("/results", json=payload)
    assert res.status_code == 201
    res_id = res.json()["id"]

    # 2. Validation error: negative score
    bad_payload = payload.copy()
    bad_payload["score"] = -5.0
    res_bad = client.post("/results", json=bad_payload)
    assert res_bad.status_code == 422

    # 3. Validation error: non-existent athlete
    bad_athlete_payload = payload.copy()
    bad_athlete_payload["athlete_id"] = 9999
    res_no_a = client.post("/results", json=bad_athlete_payload)
    assert res_no_a.status_code == 404

    # 4. GET /results/{id}
    res_get = client.get(f"/results/{res_id}")
    assert res_get.status_code == 200
    assert res_get.json()["score"] == 10.25

    # 5. PATCH /results/{id}
    res_patch = client.patch(f"/results/{res_id}", json={"score": 10.15})
    assert res_patch.status_code == 200
    assert res_patch.json()["score"] == 10.15

    # 6. DELETE /results/{id}
    assert client.delete(f"/results/{res_id}").status_code == 204
    assert client.get(f"/results/{res_id}").status_code == 404


def test_sport_analytics_and_ranking(client: TestClient, seed_data: dict[str, Any]) -> None:
    sprint_id = seed_data["sports"][0].id  # Біг на 100м (is_lower_better=True)

    # 1. GET /sports/{id}/results with query filter
    res_filtered = client.get(f"/sports/{sprint_id}/results", params={"min_score": 10.0, "max_score": 11.0})
    assert res_filtered.status_code == 200
    results_list = res_filtered.json()
    assert len(results_list) == 1
    assert results_list[0]["score"] == 10.35

    # 2. GET /sports/{id}/ranking
    res_rank = client.get(f"/sports/{sprint_id}/ranking")
    assert res_rank.status_code == 200
    rank_data = res_rank.json()
    assert rank_data["sport_name"] == "Біг на 100м"
    assert rank_data["total_results"] == 2
    assert rank_data["best_score"] == 10.35
    assert rank_data["ranking"][0]["rank"] == 1
    assert rank_data["ranking"][0]["athlete_name"] == "Данило Гарбіч"
    assert rank_data["ranking"][1]["rank"] == 2

    # 3. GET /sports/{id}/statistics
    res_stats = client.get(f"/sports/{sprint_id}/statistics")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_results"] == 2
    assert stats["min_score"] == 10.35
    assert stats["max_score"] == 11.20
    assert abs(stats["avg_score"] - 10.78) <= 0.02


def test_batch_rankings_endpoint(client: TestClient, seed_data: dict[str, Any]) -> None:
    s1_id = seed_data["sports"][0].id
    s2_id = seed_data["sports"][1].id

    # POST /sports/rankings/batch
    res = client.post("/sports/rankings/batch", json={"sport_ids": [s1_id, s2_id, 9999]})
    assert res.status_code == 200
    batch_data = res.json()
    assert batch_data["total_requested"] == 3
    assert batch_data["successful"] == 2
    assert len(batch_data["rankings"]) == 2
