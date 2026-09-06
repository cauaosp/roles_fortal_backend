import asyncio
import json

from utils.functions import dataclass_asdict, fetch_concurrent


async def main():
    newspaperData = await fetch_concurrent(limit=4)  # 4 scraping simultâneos
    resultAsDict = dataclass_asdict(newspaperData)
    return resultAsDict


if __name__ == "__main__":
    data = asyncio.run(main())

    with open("data/artigos_ceara.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print("Arquivo salvo!")
