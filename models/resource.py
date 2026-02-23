"""Resource model."""

from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class ResourceType:
    WORK = "work"
    MATERIAL = "material"
    COST = "cost"
    ALL = [WORK, MATERIAL, COST]
    LABELS = {
        WORK: "作業",
        MATERIAL: "資材",
        COST: "コスト",
    }


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), default="New Resource")
    resource_type: Mapped[str] = mapped_column(String(20), default=ResourceType.WORK)
    max_units: Mapped[float] = mapped_column(Float, default=100.0)  # percentage
    standard_rate: Mapped[float] = mapped_column(Float, default=0.0)
    overtime_rate: Mapped[float] = mapped_column(Float, default=0.0)
    cost_per_use: Mapped[float] = mapped_column(Float, default=0.0)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    assignments = relationship("Assignment", back_populates="resource", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resource(id={self.id}, name='{self.name}', type='{self.resource_type}')>"
