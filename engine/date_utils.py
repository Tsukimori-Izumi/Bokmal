"""Date utilities for working day calculations."""

from datetime import date, timedelta

from config import DEFAULT_WORKING_DAYS


def is_working_day(d: date, working_days: list[int] | None = None,
                   holidays: set[date] | None = None) -> bool:
    """Check if a given date is a working day."""
    if working_days is None:
        working_days = DEFAULT_WORKING_DAYS
    if holidays is None:
        holidays = set()
    return d.weekday() in working_days and d not in holidays


def add_working_days(start: date, days: int,
                     working_days: list[int] | None = None,
                     holidays: set[date] | None = None) -> date:
    """Add working days to a start date and return the resulting date."""
    if days <= 0:
        return start
    current = start
    remaining = days - 1  # start date counts as day 1
    while remaining > 0:
        current += timedelta(days=1)
        if is_working_day(current, working_days, holidays):
            remaining -= 1
    # Make sure we land on a working day
    while not is_working_day(current, working_days, holidays):
        current += timedelta(days=1)
    return current


def subtract_working_days(end: date, days: int,
                          working_days: list[int] | None = None,
                          holidays: set[date] | None = None) -> date:
    """Subtract working days from an end date."""
    if days <= 0:
        return end
    current = end
    remaining = days - 1
    while remaining > 0:
        current -= timedelta(days=1)
        if is_working_day(current, working_days, holidays):
            remaining -= 1
    while not is_working_day(current, working_days, holidays):
        current -= timedelta(days=1)
    return current


def count_working_days(start: date, end: date,
                       working_days: list[int] | None = None,
                       holidays: set[date] | None = None) -> int:
    """Count the number of working days between two dates (inclusive)."""
    if start > end:
        return 0
    count = 0
    current = start
    while current <= end:
        if is_working_day(current, working_days, holidays):
            count += 1
        current += timedelta(days=1)
    return max(1, count)


def get_date_range(tasks_data: list[dict]) -> tuple[date, date]:
    """Get the min start and max end date from a list of tasks."""
    starts = [t["start_date"] for t in tasks_data if t.get("start_date")]
    ends = [t["end_date"] for t in tasks_data if t.get("end_date")]
    if not starts or not ends:
        today = date.today()
        return today, today + timedelta(days=30)
    return min(starts), max(ends)
