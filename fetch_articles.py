import asyncio
import json

from infrastructure.services.insert_articles import save_articles_to_db
from utils.execution import dataclass_asdict, dict_articles, fetch_concurrent


async def fetch_articles() -> dict:
    newspaperData = await fetch_concurrent(limit=4)  # 4 scraping simultâneos
    resultAsDict = dataclass_asdict(newspaperData)

    with open("data/artigos_ceara.json", "w", encoding="utf-8") as f:
        json.dump(resultAsDict, f, ensure_ascii=False, indent=4)
        print("Arquivo salvo!")

    return resultAsDict


if __name__ == "__main__":
    data = asyncio.run(fetch_articles())
    print("Fetched articles!")
    articles = dict_articles()
    print(f"Found {len(articles)} articles!")
    save_articles_to_db(articles)
