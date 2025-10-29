from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class DataStatus(BaseModel):
    total_countries: int | None
    last_refreshed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CountryData(BaseModel):
    id: int
    name: str
    capital: Optional[str]
    region: Optional[str]
    population: int
    currency_code: Optional[str]
    exchange_rate: Optional[float]
    estimated_gdp: Optional[float]
    flag_url: Optional[str]
    last_refreshed_at: datetime

    model_config = ConfigDict(from_attributes=True)


