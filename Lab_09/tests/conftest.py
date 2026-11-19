"""Фікстури pytest для підготовки тестових даних та тимчасових файлів."""

import json
from pathlib import Path
from typing import Generator, List
import pytest
from sports_opt.analytics import generate_sports_dataset
from sports_opt.models import SportResult


@pytest.fixture(scope="session")
def sample_sports_data() -> List[SportResult]:
    """Генерує еталонний набір даних із 1000 записів для швидких тестів."""
    return generate_sports_dataset(1_000, seed=42)


@pytest.fixture(scope="session")
def sample_scores(sample_sports_data: List[SportResult]) -> List[float]:
    """Список числових балів з еталонного набору даних."""
    return [r.score for r in sample_sports_data]


@pytest.fixture(scope="function")
def temp_json_files(tmp_path: Path) -> Generator[List[Path], None, None]:
    """Створює тимчасові JSON-файли для тестування паралельного зчитування."""
    file_paths: List[Path] = []
    for i in range(3):
        p = tmp_path / f"batch_{i}.json"
        items = [{"id": j, "score": float(j * 1.5)} for j in range(10)]
        p.write_text(json.dumps(items), encoding="utf-8")
        file_paths.append(p)
    yield file_paths
