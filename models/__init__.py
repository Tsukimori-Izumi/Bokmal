"""UniTK Data Models Package."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


def init_db():
    """Create all tables."""
    from models.project import Project  # noqa: F401
    from models.task import Task  # noqa: F401
    from models.dependency import Dependency  # noqa: F401
    from models.resource import Resource  # noqa: F401
    from models.assignment import Assignment  # noqa: F401
    from models.calendar import Calendar, CalendarException  # noqa: F401
    Base.metadata.create_all(engine)


def get_session():
    """Get a new database session."""
    return Session()
