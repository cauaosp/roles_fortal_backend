import asyncio
import json

from utils.functions import fetch_concurrent


async def main():
    resultados = await fetch_concurrent(limit=4)  # 4 scraping simultâneos
    return resultados


if __name__ == "__main__":
    data = asyncio.run(main())

    with open("data/artigos_ceara.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print("Arquivo salvo!")

    print(f"total: {sum(len(v) for v in data.values())} artigos")
    print({k: len(v) for k, v in data.items()})
