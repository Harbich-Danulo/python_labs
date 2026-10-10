"""Main application module and entry point for Sports Results Tracker."""

import sys
from sports_tracker.models import Athlete, InvalidAthleteDataError
from sports_tracker.services import (
    add_result,
    calculate_average_result,
    calculate_statistics,
    filter_by_multiple_criteria,
    filter_by_sport,
    find_best_result,
    generate_ranking,
)


def create_demo_athletes() -> list[Athlete]:
    """Create a default list of athletes for demonstration."""
    return [
        Athlete(
            name="Ярослава Магучіх",
            sport="Стрибки у висоту",
            result=2.10,
            category="Дорослі",
        ),
        Athlete(
            name="Ірина Геращенко",
            sport="Стрибки у висоту",
            result=2.00,
            category="Дорослі",
        ),
        Athlete(
            name="Юлія Левченко",
            sport="Стрибки у висоту",
            result=1.95,
            category="Дорослі",
        ),
        Athlete(
            name="Олег Верняєв",
            sport="Спортивна гімнастика",
            result=15.30,
            category="Майстри",
        ),
        Athlete(
            name="Ілля Ковтун",
            sport="Спортивна гімнастика",
            result=15.65,
            category="Юніори",
        ),
        Athlete(
            name="Михайло Романчук",
            sport="Плавання",
            result=880.20,
            category="Дорослі",
        ),
        Athlete(
            name="Олександр Желтяков",
            sport="Плавання",
            result=895.10,
            category="Юніори",
        ),
    ]


def print_athletes(athletes: list[Athlete], title: str = "Список спортсменів") -> None:
    """Print a formatted table of athletes.

    Args:
        athletes: List of athletes to display.
        title: Table header title.
    """
    print(f"\n=== {title} ===")
    if not athletes:
        print("Записів не знайдено.")
        return

    header = f"{'№':<4} | {'Ім\'я спортсмена':<24} | {'Вид спорту':<22} | {'Результат':<10} | {'Категорія':<12}"
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)

    for idx, athlete in enumerate(athletes, start=1):
        print(
            f"{idx:<4} | {athlete.name:<24} | {athlete.sport:<22} | "
            f"{athlete.result:<10.2f} | {athlete.category:<12}"
        )
    print(separator)


def prompt_non_empty_string(prompt_text: str) -> str:
    """Prompt user for a non-empty string with validation."""
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Помилка: поле не може бути порожнім. Спробуйте ще раз.")


def prompt_positive_float(prompt_text: str) -> float:
    """Prompt user for a positive float number with validation."""
    while True:
        raw_val = input(prompt_text).strip()
        try:
            val = float(raw_val)
            if val < 0:
                print("Помилка: результат не може бути від'ємним числом.")
                continue
            return val
        except ValueError:
            print("Помилка: введіть коректне числове значення (наприклад: 15.5 або 2.05).")


def handle_add_athlete(athletes: list[Athlete]) -> None:
    """Interactively input and register a new athlete."""
    print("\n--- Додавання нового спортивного результату ---")
    name = prompt_non_empty_string("Введіть ім'я та прізвище спортсмена: ")
    sport = prompt_non_empty_string("Введіть вид спорту: ")
    result = prompt_positive_float("Введіть числовий результат (очки / метри / бали / секунди): ")
    category = prompt_non_empty_string("Введіть категорію (напр. Дорослі, Юніори, Майстри): ")

    try:
        new_athlete = Athlete(name=name, sport=sport, result=result, category=category)
        add_result(athletes, new_athlete)
        print(f"Успішно додано: {new_athlete.name} ({new_athlete.sport})!")
    except InvalidAthleteDataError as err:
        print(f"Помилка валідації даних: {err}")


def handle_filter_by_sport(athletes: list[Athlete]) -> None:
    """Search and filter athletes by sport."""
    sport = prompt_non_empty_string("\nВведіть вид спорту для пошуку: ")
    filtered = filter_by_sport(athletes, sport)
    print_athletes(filtered, f"Результати за видом спорту: '{sport}'")


def handle_multi_search(athletes: list[Athlete]) -> None:
    """Filter by multiple criteria: sport and category."""
    print("\n--- Пошук за кількома критеріями (порожнє значення — пропустити) ---")
    sport = input("Вид спорту (Enter для пропуску): ").strip() or None
    category = input("Категорія (Enter для пропуску): ").strip() or None

    filtered = filter_by_multiple_criteria(athletes, sport=sport, category=category)
    crit_info = f"Спорт='{sport or '*'}' | Категорія='{category or '*'}'"
    print_athletes(filtered, f"Результати пошуку ({crit_info})")


def handle_best_result(athletes: list[Athlete]) -> None:
    """Find and display the best result."""
    sport_filter = input("\nВведіть вид спорту (або натисніть Enter для пошуку серед усіх): ").strip() or None
    best = find_best_result(athletes, sport=sport_filter)
    if best is None:
        print("Спортсменів не знайдено.")
    else:
        sport_msg = f" у спорті '{sport_filter}'" if sport_filter else " серед усіх"
        print(f"\nНайкращий результат{sport_msg}:")
        print(f"  Спортсмен: {best.name}")
        print(f"  Вид спорту: {best.sport}")
        print(f"  Результат:  {best.result:.2f}")
        print(f"  Категорія:  {best.category}")


def handle_statistics(athletes: list[Athlete]) -> None:
    """Display average result and statistics."""
    sport_filter = input("\nВведіть вид спорту (або Enter для загальної статистики): ").strip() or None
    stats = calculate_statistics(athletes, sport=sport_filter)
    scope = f"для спорту '{sport_filter}'" if sport_filter else "загальні"
    print(f"\nСтатистичні показники ({scope}):")
    print(f"  Кількість учасників: {stats['count']}")
    print(f"  Середній результат:  {stats['average']:.2f}")
    print(f"  Мінімальний показник: {stats['min_result']:.2f}")
    print(f"  Максимальний показник: {stats['max_result']:.2f}")


def handle_ranking(athletes: list[Athlete]) -> None:
    """Show ranking sorted by result."""
    sport_filter = input("\nВведіть вид спорту для рейтингу (або Enter для загального): ").strip() or None
    ranked = generate_ranking(athletes, sport=sport_filter, descending=True)
    title = f"Рейтинг спортсменів ({sport_filter if sport_filter else 'Загальний'})"
    print_athletes(ranked, title)


def print_menu() -> None:
    """Print the interactive main menu."""
    print("\n" + "=" * 50)
    print("      СИСТЕМА ОБЛІКУ СПОРТИВНИХ РЕЗУЛЬТАТІВ       ")
    print("=" * 50)
    print("1. Показати всі спортивні результати")
    print("2. Додати новий результат (введення з клавіатури)")
    print("3. Пошук результатів за видом спорту")
    print("4. Пошук за декількома критеріями (спорт + категорія)")
    print("5. Визначити найкращий результат")
    print("6. Розрахувати середній результат та статистику")
    print("7. Сформувати рейтинг спортсменів")
    print("0. Вихід із програми")
    print("=" * 50)


def run_menu(athletes: list[Athlete]) -> None:
    """Main application loop with console menu."""
    while True:
        print_menu()
        choice = input("Оберіть пункт меню (0-7): ").strip()

        if choice == "1":
            print_athletes(athletes, "Усі зареєстровані результати")
        elif choice == "2":
            handle_add_athlete(athletes)
        elif choice == "3":
            handle_filter_by_sport(athletes)
        elif choice == "4":
            handle_multi_search(athletes)
        elif choice == "5":
            handle_best_result(athletes)
        elif choice == "6":
            handle_statistics(athletes)
        elif choice == "7":
            handle_ranking(athletes)
        elif choice == "0":
            print("\nДякуємо за використання програми. До побачення!")
            break
        else:
            print("Невідома команда. Будь ласка, оберіть цифру від 0 до 7.")


def run_demo_scenario(athletes: list[Athlete]) -> None:
    """Automated demonstration of key business logic features."""
    print("\n--- ДЕМОНСТРАЦІЙНИЙ СЦЕНАРІЙ (АВТОМАТИЧНИЙ ЗАПУСК) ---")
    print_athletes(athletes, "Початковий список спортсменів")

    sport = "Стрибки у висоту"
    print(f"\n[1] Фільтрація за видом спорту: '{sport}'")
    jumpers = filter_by_sport(athletes, sport)
    print_athletes(jumpers, f"Спортсмени ({sport})")

    print(f"\n[2] Найкращий результат у виді '{sport}':")
    best = find_best_result(athletes, sport)
    if best:
        print(f"    -> {best.name} з результатом {best.result:.2f} м ({best.category})")

    avg = calculate_average_result(athletes, sport)
    print(f"\n[3] Середній результат у виді '{sport}': {avg:.2f}")

    print(f"\n[4] Рейтинг спортсменів у виді '{sport}':")
    ranked = generate_ranking(athletes, sport)
    for pos, ath in enumerate(ranked, start=1):
        print(f"    {pos}. {ath.name:<20} : {ath.result:.2f} ({ath.category})")

    print("\n[5] Пошук за декількома критеріями (Спортивна гімнастика + Юніори):")
    multi = filter_by_multiple_criteria(athletes, sport="Спортивна гімнастика", category="Юніори")
    print_athletes(multi, "Результати складного пошуку")


def main() -> None:
    """Application entry point."""
    athletes = create_demo_athletes()

    # If launched with --demo argument, run non-interactive demo
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo_scenario(athletes)
        return

    print("\nЛаскаво просимо до Системи обліку спортивних результатів!")
    print("Лабораторна робота №1 з дисципліни 'Професійний Python'.")
    run_menu(athletes)


if __name__ == "__main__":
    main()
