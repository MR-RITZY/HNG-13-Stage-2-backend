from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class CurrencyExchange(Base):
    __tablename__ = "countries_currency_and_exchange"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    capital: Mapped[str] = mapped_column(String(255), nullable=True)
    region: Mapped[str] = mapped_column(String(255), nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=True)
    exchange_rate: Mapped[float] = mapped_column(Float, nullable=True)
    estimated_gdp: Mapped[float] = mapped_column(Float, nullable=True)
    flag_url: Mapped[str] = mapped_column(String(512), nullable=True)
    last_refreshed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
