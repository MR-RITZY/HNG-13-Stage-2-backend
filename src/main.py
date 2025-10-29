from fastapi import FastAPI, Depends, status, Query
from contextlib import asynccontextmanager, AsyncExitStack
from typing import Annotated, Optional, List
from fastapi.responses import FileResponse, Response
import os.path


from src.image import create_image
from src.log import app_info
from src.db import db_lifespan
from src.exc import ServiceUnavailableError, DataNotFoundException, register_exc
from src.service import get_curreny_exchange_service, CurrencyExchangeServices
from src.schema import DataStatus, CountryData
from src.utils import process_orm_to_text

currency_exchange_service = Annotated[
    CurrencyExchangeServices, Depends(get_curreny_exchange_service)
]


SORT_PATTERN = r"""^(:?(:?name|population|gdp|rate|capital|region)_(:?asc|desc))|
(:?(:?asc|desc)_(:?name|population|gdp|rate|capital|region))$"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        app_info.info("Setting Up APP's Start-ups")
        await stack.enter_async_context(db_lifespan())
        app_info.info("APP's Start-ups Successfully Completed")
        yield
        app_info.info("Shutting Down --- Cleaning Up APP's Resources")


app = FastAPI(lifespan=lifespan)
register_exc(app)



@app.post("/countries/refresh", response_model=List[CountryData], status_code=status.HTTP_201_CREATED)
async def insert_or_update_data(currency_exchange: currency_exchange_service):
    result = await currency_exchange.update_econ_data()
    if not result:
        raise ServiceUnavailableError(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch data from External APIs",
        )
    orm = await currency_exchange.data_summary()
    text = process_orm_to_text(orm)
    create_image(text)
    return result


@app.get("/countries", response_model=List[CountryData])
async def get_countries(
    currency_exchange: currency_exchange_service,
    name: Optional[str] = Query(None),
    capital: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    population: Optional[int] = Query(None),
    min_population: Optional[int] = Query(None),
    max_population: Optional[int] = Query(None),
    gdp: Optional[float] = Query(None),
    min_gdp: Optional[float] = Query(None),
    max_gdp: Optional[float] = Query(None),
    rate: Optional[float] = Query(None),
    min_rate: Optional[float] = Query(None),
    max_rate: Optional[float] = Query(None),
    sort: Optional[str] = Query(None, regex=SORT_PATTERN),
):

    filters = {
        "name": name,
        "capital": capital,
        "region": region,
        "currency_code": currency,
        "population": population,
        "min_population": min_population,
        "max_population": max_population,
        "rate": rate,
        "min_rate": min_rate,
        "max_rate": max_rate,
        "gdp": gdp,
        "min_gdp": min_gdp,
        "max_gdp": max_gdp,
        "sort": sort,
    }
    data = await currency_exchange.get_data_by_conditions(filters)
    if not data:
        raise DataNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match Not Found"
        )
    return data


@app.get("/countries/image")
async def get_image():
    img_path = "cache/summary.png"
    if not os.path.exists(img_path):
        raise DataNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary image not found",
        )
    return FileResponse(img_path, media_type="image/png")

@app.get("/countries/:{name}", response_model=CountryData)
async def get_country_by_name(name: str, currency_exchange: currency_exchange_service):
    country = await currency_exchange.get_country_by_name(name.lower())
    if not country:
        raise DataNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified Country Not in Database",
        )
    return country

@app.get("/status", response_model=DataStatus)
async def get_status(currency_exchange: currency_exchange_service):
    result = await currency_exchange.get_data_status()
    total = result[0] if result else 0
    last = result[1] if result else None
    return DataStatus(total_countries=total, last_refreshed_at=last)



@app.delete("/countries/:{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(name:str, currency_exchange: currency_exchange_service):
    result = await currency_exchange.delete_by_country_name(name.lower())
    if not result:
        raise DataNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Specified Country Not in Database"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)