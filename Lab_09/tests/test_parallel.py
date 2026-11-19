"""Тестування паралельної обробки: потоки, процеси, пули та синхронізація."""

import threading
from pathlib import Path
from typing import List
import pytest
from sports_opt.analytics import calculate_scores_sequential
from sports_opt.parallel import (
    ThreadSafeResultTracker,
    calculate_scores_processes,
    calculate_scores_threads,
    load_dataset_files_parallel,
    load_dataset_files_sequential,
)


def test_thread_pool_correctness(sample_scores: List[float]) -> None:
    subset = sample_scores[:30]
    seq_res = calculate_scores_sequential(subset)
    th_res = calculate_scores_threads(subset, workers=2)

    for s, t in zip(seq_res, th_res):
        assert t == pytest.approx(s, rel=1e-5)


def test_process_pool_correctness(sample_scores: List[float]) -> None:
    subset = sample_scores[:30]
    seq_res = calculate_scores_sequential(subset)
    pr_res = calculate_scores_processes(subset, workers=2, chunksize=10)

    for s, p in zip(seq_res, pr_res):
        assert p == pytest.approx(s, rel=1e-5)


def test_parallel_file_loading(temp_json_files: List[Path]) -> None:
    seq_items = load_dataset_files_sequential(temp_json_files)
    par_items = load_dataset_files_parallel(temp_json_files, workers=2)

    assert len(seq_items) == 30
    assert len(par_items) == 30
    assert [x["id"] for x in seq_items] == [x["id"] for x in par_items]


def test_thread_safe_result_tracker() -> None:
    tracker = ThreadSafeResultTracker()
    num_threads = 4
    count_per_thread = 500

    def worker() -> None:
        for _ in range(count_per_thread):
            tracker.increment_safe()

    threads = [
        threading.Thread(target=worker)
        for _ in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert tracker.counter == num_threads * count_per_thread
