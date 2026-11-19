"""ORM-моделі бази даних SQLAlchemy 2.0 для предметної області «Облік спортивних результатів»."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовий декларативний клас SQLAlchemy."""
    pass


class Sport(Base):
    """Модель виду спорту."""

    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    is_lower_better: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    results: Mapped[List["Result"]] = relationship(
        "Result", back_populates="sport", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sport(id={self.id}, name='{self.name}', unit='{self.unit}', is_lower_better={self.is_lower_better})>"


class Athlete(Base):
    """Модель спортсмена."""

    __tablename__ = "athletes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), default="Україна", nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    results: Mapped[List["Result"]] = relationship(
        "Result", back_populates="athlete", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Athlete(id={self.id}, name='{self.name}', country='{self.country}', age={self.age})>"


class Result(Base):
    """Модель спортивного результату зі зв'язками до спортсмена та виду спорту."""

    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    athlete_id: Mapped[int] = mapped_column(
        ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sport_id: Mapped[int] = mapped_column(
        ForeignKey("sports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    competition_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    athlete: Mapped["Athlete"] = relationship("Athlete", back_populates="results")
    sport: Mapped["Sport"] = relationship("Sport", back_populates="results")

    def __repr__(self) -> str:
        return (
            f"<Result(id={self.id}, athlete_id={self.athlete_id}, "
            f"sport_id={self.sport_id}, score={self.score}, category='{self.category}')>"
        )
