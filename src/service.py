from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import select, func, delete
from src.db import get_db
from fastapi import Depends
from typing import Annotated
from datetime import datetime, timezone

from src.model import CurrencyExchange
from src.utils import get_and_compute_countries_data, strip_orders
from src.log import app_error

db = Annotated[AsyncSession, Depends(get_db)]

field_map = {
    "name": CurrencyExchange.name,
    "capital": CurrencyExchange.capital,
    "region": CurrencyExchange.region,
    "population": CurrencyExchange.population,
    "gdp": CurrencyExchange.estimated_gdp,
    "rate": CurrencyExchange.exchange_rate,
}

filter_map = {
    "name": lambda v: CurrencyExchange.name.ilike(f"%{v}%"),
    "capital": lambda v: CurrencyExchange.capital.ilike(f"%{v}%"),
    "region": lambda v: CurrencyExchange.region.ilike(f"%{v}%"),
    "currency_code": lambda v: CurrencyExchange.currency_code.ilike(f"{v}"),
    "population": lambda v: CurrencyExchange.population == v,
    "min_population": lambda v: CurrencyExchange.population >= v,
    "max_population": lambda v: CurrencyExchange.population <= v,
    "gdp": lambda v: CurrencyExchange.estimated_gdp == v,
    "min_gdp": lambda v: CurrencyExchange.estimated_gdp >= v,
    "max_gdp": lambda v: CurrencyExchange.estimated_gdp <= v,
    "rate": lambda v: CurrencyExchange.exchange_rate == v,
    "min_rate": lambda v: CurrencyExchange.exchange_rate >= v,
    "max_rate": lambda v: CurrencyExchange.exchange_rate <= v,
}


class CurrencyExchangeServices:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_econ_data(self):
        try:
            data_list = await get_and_compute_countries_data()
            last_refreshed_at = datetime.now(tz=timezone.utc)
            if data_list:
                stmt = insert(CurrencyExchange).values(data_list)
                stmt = stmt = stmt.on_duplicate_key_update(
                    capital=stmt.inserted.capital,
                    region=stmt.inserted.region,
                    population=stmt.inserted.population,
                    currency_code=stmt.inserted.currency_code,
                    exchange_rate=stmt.inserted.exchange_rate,
                    estimated_gdp=stmt.inserted.estimated_gdp,
                    flag_url=stmt.inserted.flag_url,
                    last_refreshed_at=stmt.inserted.last_refreshed_at,
                )
                await self.db.execute(stmt)
                await self.db.commit()
                
                return await self.get_all()
        except Exception as e:
            app_error.error(f"Error Encoutered while updating the Database: {e}")
            await self.db.rollback()

    async def get_data_by_conditions(self, conditions: dict):
        filter_list = []
        for key, value in conditions.items():
            if value and key != "sort":
                filter = filter_map[key](value)
                filter_list.append(filter)
        stmt = select(CurrencyExchange)
        if conditions.get("sort"):
            sort = conditions["sort"]
            sort_string = strip_orders(sort)
            stmt = stmt.where(*filter_list).order_by(field_map[sort_string])
        else:
            stmt = stmt.where(*filter_list)
        result = await self.db.scalars(stmt)
        return result.all()

    async def get_country_by_name(self, name: str):
        scalar_result = await self.db.scalars(
            select(CurrencyExchange).where(CurrencyExchange.name == name)
        )
        result = scalar_result.first()
        if result:
            return result
        result = await self.db.scalars(
            select(CurrencyExchange).where(CurrencyExchange.name.ilike(f"%{name}%"))
        )
        return result.first()

    async def get_data_status(self):
        stmt = select(
            func.count(CurrencyExchange.id),
            func.max(CurrencyExchange.last_refreshed_at),
        )
        result = await self.db.execute(stmt)
        return result.one_or_none()

    async def data_summary(self):
        stmt = (
            select(
                CurrencyExchange,
                func.count(CurrencyExchange.id).over().label("total_count"),
                func.max(CurrencyExchange.last_refreshed_at)
                .over()
                .label("last_time_refresh"),
            )
            .order_by(CurrencyExchange.estimated_gdp.desc())
            .limit(5)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def delete_by_country_name(self, name: str):
        stmt = (
            delete(CurrencyExchange)
            .where(CurrencyExchange.name == name)
            .execution_options(synchronize_session=False)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def get_all(self):
        result = await self.db.scalars(select(CurrencyExchange))
        return result.all()


def get_curreny_exchange_service(db: db):
    return CurrencyExchangeServices(db)
