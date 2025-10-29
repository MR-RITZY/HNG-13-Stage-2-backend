from httpx import AsyncClient
import random
from typing import List
from datetime import datetime

from src.log import app_error, app_info


countries_data_url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
exchange_rate_url = "https://open.er-api.com/v6/latest/USD"


async def get_api(url: str):
    try:
        async with AsyncClient() as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
            app_info.info(f"Unsuccessfully response:{url} --- {resp.status_code}")
    except Exception:
        app_error.error(
            f"Unable to Connect to or get data from the specified URL: {url}"
        )


async def get_and_compute_countries_data(last_refreshed_at: datetime):
    countries_data_list = []
    countries_data = await get_api(countries_data_url)
    exchange_rate_data = await get_api(exchange_rate_url)
    if not countries_data or not exchange_rate_data:
        return None
    exchange_rates = exchange_rate_data.get("rates")
    if not exchange_rates:
        return None

    for data in countries_data:
        name = data.get("name")
        population = data.get("population")
        if not name or not population:
            continue
        currency_data = data.get("currencies")
        if not currency_data or not currency_data[0].get("code"):
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0
        else:
            currency_code = currency_data[0].get("code")
            exchange_rate = exchange_rates.get(currency_code, None)
            if not exchange_rate:
                exchange_rate = None
                estimated_gdp = None
            else:
                multiplier = random.uniform(1000, 2000)
                estimated_gdp = (population * multiplier) / exchange_rate

        country_data = {
            "name": name.lower(),
            "capital": data["capital"].lower() if data.get("capital") else None,
            "region": data["region"].lower() if data.get("region") else None,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": data.get("flag"),
            "last_refreshed_at": last_refreshed_at,
        }
        countries_data_list.append(country_data)
    return countries_data_list


def process_orm_to_text(result: List):
    if not result:
        return "No data available"

    total_count = getattr(result[0], "total_count", None) or 0
    last_refresh_obj = getattr(result[0], "last_time_refresh", None)
    last_refresh = last_refresh_obj.isoformat() if last_refresh_obj else "N/A"

    text_output = (
        "Top 5 Countries with the Highest GDP (Descending Order)\n"
        + "=" * 100 + "\n"
    )

    text_output += (
        f"{'S/N':<4} {'Name':<40} {'Capital':<20} {'Region':<20} "
        f"{'Population':<20} {'Currency':<20} {'GDP (USD)':<20}\n"
    )
    text_output += "-" * 200 + "\n"

    for i, row in enumerate(result, start=1):
        country = row.CurrencyExchange
        name = (country.name or "")[:24]
        capital = (country.capital or "")[:11]
        region = (country.region or "")[:11]
        population = int(country.population) if country.population else 0
        currency_code = country.currency_code or ""
        estimated_gdp = float(country.estimated_gdp) if country.estimated_gdp else 0.0

        text_output += (
            f"{i:<4}"
            f"{name:<40}"
            f"{capital:<20}"
            f"{region:<20}"
            f"{population:<20,}"
            f"{currency_code:<20}"
            f"{estimated_gdp:<20,.2f}\n"
        )

    text_output += "=" * 100 + "\n"
    text_output += f"Total Countries: {total_count}\n"
    text_output += f"Last Refreshed At: {last_refresh}\n"

    return text_output


def strip_orders(string: str):
    if string.startswith("asc_"):
        return string[len("asc_"):]
    if string.startswith("desc_"):
        return string[len("desc_"):]
    if string.endswith("_asc"):
        return string[:-len("_asc")]
    if string.endswith("_desc"):
        return string[:-len("_desc")]
    return string