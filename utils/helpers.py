import re
from datetime import datetime, timedelta, timezone

from dateutil import parser


def creation_time() -> datetime:
    fuso_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasilia)

def clear_html_string(texto):
    if not texto:
        return None

    subtitulo = re.sub(r"<[^>]+>", "", texto)
    return subtitulo[:1000].strip()

async def log_html(response, name):
    print(f"\nLOG da função: {name}")
    data = await response.text()

    if response.headers:
        print("1 - headers: ", response.headers)
    if response.status:
        print("2 - status: ", response.status)
    if data:
        print("3 - Primeiros 1000 caracteres: ", data[:1000])

    print("-*-"*20)


def normalize_publication_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None

    tz = timezone(timedelta(hours=-3))

    try:
        date = parser.parse(date_str)
        if date.tzinfo is None:
            date = date.replace(tzinfo=tz)

        return date.astimezone(tz)
    except (ValueError, TypeError, OverflowError):
        for fmt in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        ]:
            try:
                return datetime.strptime(date_str, fmt).astimezone(tz)
            except ValueError:
                continue

        print(f"⚠️ Data não pôde ser parseada: {date_str}")
        return None
