"""Модуль паралельних обчислень: потоки (threading), процеси (multiprocessing), пули та синхронізація."""

from __future__ import annotations
import json
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List
from sports_opt.analytics import score_complex_transform


def calculate_scores_threads(scores: List[float], workers: int = 4) -> List[float]:
    """Паралельна обробка через ThreadPoolExecutor (демонстрація впливу GIL на CPU-bound код)."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(score_complex_transform, scores))


def calculate_scores_processes(
    scores: List[float], workers: int = 4, chunksize: int = 1000
) -> List[float]:
    """Справжній паралелізм на багатьох ядрах процесора через ProcessPoolExecutor."""
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(score_complex_transform, scores, chunksize=chunksize))


def read_dataset_file(file_path: Path) -> List[Dict[str, Any]]:
    """I/O-bound функція зчитування одного JSON-файлу даних."""
    text = file_path.read_text(encoding="utf-8")
    data: List[Dict[str, Any]] = json.loads(text)
    return data


def load_dataset_files_sequential(file_paths: List[Path]) -> List[Dict[str, Any]]:
    """Послідовне зчитування декількох файлів (I/O-bound Baseline)."""
    combined: List[Dict[str, Any]] = []
    for fp in file_paths:
        combined.extend(read_dataset_file(fp))
    return combined


def load_dataset_files_parallel(file_paths: List[Path], workers: int = 4) -> List[Dict[str, Any]]:
    """Паралельне зчитування файлів за допомогою ThreadPoolExecutor (ефективно для I/O)."""
    combined: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for batch in executor.map(read_dataset_file, file_paths):
            combined.extend(batch)
    return combined


class ThreadSafeResultTracker:
    """Клас обліку кількості оброблених записів із демонстрацією захисту від Race Condition."""

    def __init__(self) -> None:
        self.counter: int = 0
        self.lock = threading.Lock()

    def increment_unsafe(self) -> None:
        """Небезпечне інкрементування без блокування (Race Condition)."""
        temp = self.counter
        # Штучна мікропауза для провокації перемикання контексту потоків
        for _ in range(10):
            pass
        self.counter = temp + 1

    def increment_safe(self) -> None:
        """Безпечне атомарне інкрементування через синхронізацію Lock."""
        with self.lock:
            temp = self.counter
            for _ in range(10):
                pass
            self.counter = temp + 1

    def reset(self) -> None:
        self.counter = 0
