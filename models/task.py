"""Task model."""

from datetime import date, timedelta

from sqlalchemy import String, Date, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(300), default="New Task")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=1)  # in working days
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 - 100.0
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)
    wbs: Mapped[str] = mapped_column(String(50), default="")
    wbs_level: Mapped[int] = mapped_column(Integer, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False)
    is_summary: Mapped[bool] = mapped_column(Boolean, default=False)
    constraint_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    constraint_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    manual_scheduling: Mapped[bool] = mapped_column(Boolean, default=False)

    # Baseline fields
    baseline_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    baseline_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    baseline_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    project = relationship("Project", back_populates="tasks")
    children = relationship("Task", backref="parent", remote_side="Task.id",
                            foreign_keys=[parent_id], viewonly=True)

    predecessors = relationship(
        "Dependency", foreign_keys="Dependency.successor_id",
        back_populates="successor", cascade="all, delete-orphan"
    )
    successors = relationship(
        "Dependency", foreign_keys="Dependency.predecessor_id",
        back_populates="predecessor", cascade="all, delete-orphan"
    )
    assignments = relationship("Assignment", back_populates="task", cascade="all, delete-orphan")

    @property
    def is_parent(self) -> bool:
        return self.is_summary

    @property
    def work_days(self) -> int:
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days
            return max(1, delta)
        return self.duration

    def set_dates_from_duration(self, start: date, working_days_func=None):
        """Set start and end dates based on duration."""
        self.start_date = start
        if self.is_milestone:
            self.end_date = start
            self.duration = 0
        elif working_days_func:
            self.end_date = working_days_func(start, self.duration)
        else:
            self.end_date = start + timedelta(days=max(0, self.duration - 1))

    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', wbs='{self.wbs}')>"
