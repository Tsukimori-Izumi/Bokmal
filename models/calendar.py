"""Calendar model - Working days and exceptions."""

from datetime import date

from sqlalchemy import String, Integer, Date, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from models import Base
from config import DEFAULT_WORKING_DAYS, DEFAULT_WORKING_HOURS_START, DEFAULT_WORKING_HOURS_END


class Calendar(Base):
    __tablename__ = "calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), default="Standard")
    working_days: Mapped[dict] = mapped_column(JSON, default=lambda: DEFAULT_WORKING_DAYS)
    hours_start: Mapped[int] = mapped_column(Integer, default=DEFAULT_WORKING_HOURS_START)
    hours_end: Mapped[int] = mapped_column(Integer, default=DEFAULT_WORKING_HOURS_END)

    def is_working_day(self, d: date) -> bool:
        """Check if a date is a working day."""
        if d.weekday() not in self.working_days:
            return False
        return True

    def hours_per_day(self) -> int:
        return self.hours_end - self.hours_start


class CalendarException(Base):
    __tablename__ = "calendar_exceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    calendar_id: Mapped[int] = mapped_column(Integer, nullable=False)
    exception_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_working: Mapped[bool] = mapped_column(Boolean, default=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
