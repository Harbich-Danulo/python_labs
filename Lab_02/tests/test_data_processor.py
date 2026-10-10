"""Unit tests for Laboratory Work 2 data processing module."""

from data_processor.analytics import (
    calculate_average,
    calculate_average_values,
    create_category_filter,
    create_record,
    create_result_filter,
    find_best_athlete,
    pipeline_processing,
    sort_by_result,
    universal_sort,
)
from data_processor.data import athletes
from data_processor.processors import (
    count_by_sport,
    create_id_index,
    filter_by_sport,
    get_unique_sports,
    group_by_sport,
    nested_grouping,
    universal_filter,
)


def test_unique_sports():
    sports = get_unique_sports(athletes)
    assert isinstance(sports, set)
    assert "Стрибки у висоту" in sports


def test_create_id_index():
    index = create_id_index(athletes)
    assert isinstance(index, dict)
    assert 1 in index
    assert index[1]["name"] == "Ярослава Магучіх"


def test_filter_by_sport():
    jumpers = filter_by_sport(athletes, "Стрибки у висоту")
    assert len(jumpers) == 3


def test_group_by_sport():
    grouped = group_by_sport(athletes)
    assert "Плавання" in grouped
    assert len(grouped["Плавання"]) == 2


def test_count_by_sport():
    counts = count_by_sport(athletes)
    assert counts["Стрибки у висоту"] == 3


def test_nested_grouping():
    nested = nested_grouping(athletes)
    assert "Спортивна гімнастика" in nested
    assert "Юніори" in nested["Спортивна гімнастика"]


def test_calculate_average():
    avg = calculate_average(athletes)
    assert avg > 0


def test_find_best_athlete():
    best = find_best_athlete(athletes)
    assert best is not None
    assert best["result"] == 895.10


def test_sort_by_result():
    sorted_items = sort_by_result(athletes, reverse=True)
    assert sorted_items[0]["result"] >= sorted_items[-1]["result"]


def test_args_kwargs():
    avg = calculate_average_values(10.0, 20.0, 30.0)
    assert avg == 20.0

    rec = create_record(id=10, name="Тест", sport="Біг", result=10.5)
    assert rec["name"] == "Тест"


def test_closure():
    flt = create_result_filter(100.0)
    filtered = [a for a in athletes if flt(a)]
    assert len(filtered) == 2  # 880.20, 895.10


def test_pipeline():
    stage1 = lambda data: [a for a in data if a["category"] == "Дорослі"]
    stage2 = lambda data: sorted(data, key=lambda a: a["result"])
    result = pipeline_processing(athletes, stage1, stage2)
    assert all(a["category"] == "Дорослі" for a in result)


if __name__ == "__main__":
    test_unique_sports()
    test_create_id_index()
    test_filter_by_sport()
    test_group_by_sport()
    test_count_by_sport()
    test_nested_grouping()
    test_calculate_average()
    test_find_best_athlete()
    test_sort_by_result()
    test_args_kwargs()
    test_closure()
    test_pipeline()
    print("All tests passed successfully!")
