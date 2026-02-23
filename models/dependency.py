"""Dependency model - Task relationships."""

from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class DependencyType:
    """Dependency type constants."""
    FS = "FS"  # Finish-to-Start
    SS = "SS"  # Start-to-Start
    FF = "FF"  # Finish-to-Finish
    SF = "SF"  # Start-to-Finish

    ALL = [FS, SS, FF, SF]
    LABELS = {
        FS: "終了-開始 (FS)",
        SS: "開始-開始 (SS)",
        FF: "終了-終了 (FF)",
        SF: "開始-終了 (SF)",
    }


class Dependency(Base):
    __tablename__ = "dependencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    predecessor_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    successor_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    dep_type: Mapped[str] = mapped_column(String(2), default=DependencyType.FS)
    lag: Mapped[float] = mapped_column(Float, default=0.0)  # in days, negative = lead

    predecessor = relationship("Task", foreign_keys=[predecessor_id], back_populates="successors")
    successor = relationship("Task", foreign_keys=[successor_id], back_populates="predecessors")

    @property
    def label(self):
        lag_str = ""
        if self.lag > 0:
            lag_str = f"+{self.lag}d"
        elif self.lag < 0:
            lag_str = f"{self.lag}d"
        return f"{self.predecessor_id}{self.dep_type}{lag_str}"

    def __repr__(self):
        return f"<Dependency({self.predecessor_id} -> {self.successor_id}, {self.dep_type}, lag={self.lag})>"
