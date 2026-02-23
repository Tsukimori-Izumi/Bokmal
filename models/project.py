"""Project model."""

from datetime import date

from sqlalchemy import String, Date, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), default="New Project")
    start_date: Mapped[date] = mapped_column(Date, default=date.today)
    calendar_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan",
                         order_by="Task.sort_order")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
