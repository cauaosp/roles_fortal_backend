
import re
from datetime import datetime, timedelta, timezone


def creation_time() -> datetime:
    fuso_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasilia)

def clear_html_string(texto):
    if not texto:
        return None

    subtitulo = re.sub(r"<[^>]+>", "", texto)
    return subtitulo[:250].strip()

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
