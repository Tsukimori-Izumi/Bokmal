"""Assignment model - Resource to Task mapping."""

from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"), nullable=False)
    units: Mapped[float] = mapped_column(Float, default=100.0)  # percentage
    work: Mapped[float] = mapped_column(Float, default=0.0)  # hours

    task = relationship("Task", back_populates="assignments")
    resource = relationship("Resource", back_populates="assignments")

    def __repr__(self):
        return f"<Assignment(task={self.task_id}, resource={self.resource_id}, units={self.units}%)>"
