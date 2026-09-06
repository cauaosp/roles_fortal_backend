import asyncio
import time
from dataclasses import asdict
from typing import Any

import aiohttp
from scrapers import (
    fetch_cearaagora,
    fetch_dn,
    fetch_jangadeiro,
    fetch_oestadoce,
    fetch_opovo,
    fetch_tce,
    fetch_terra_da_luz,
    fetch_verdemares,
)
from utils.const import JORNAIS_MAP


async def scraping_limitado(session, semaphore, nome: str, config: dict[str, Any]):
    async with semaphore:
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Iniciando: {nome}")
        try:
            func = config["func"]
            urlParameters = config["urlParameters"]

            if "params" in urlParameters and "headers" in urlParameters:
                resultado = await func(
                    session, urlParameters["url"], urlParameters.get("params", {}), urlParameters["headers"]
                )
            elif "params" not in urlParameters and "headers" in urlParameters:
                resultado = await func(session, urlParameters["url"], urlParameters["headers"])
            else:
                resultado = await func(session, urlParameters["url"])

            print(
                f"[{time.strftime('%H:%M:%S')}] ✅ Fim: {nome} - {len(resultado)} artigos"
            )

            return nome, resultado
        except KeyError as e:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Erro em {nome}: {e}")
            import traceback

            traceback.print_exc()
            return nome, []

async def fetch_concurrent(limit: int = 4):
    data = {nome: [] for nome in FUNCTIONS_MAP}

    semaphore = asyncio.Semaphore(limit)

    inicio = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tarefas = [
            scraping_limitado(session, semaphore, nome, config)
            for nome, config in FUNCTIONS_MAP.items()
        ]

        resultados = await asyncio.gather(*tarefas)

    final = time.perf_counter()

    tempo_total = final - inicio

    for nome, artigos in resultados:
        data[nome].extend(artigos)

    total_artigos = sum(len(artigos) for artigos in data.values())
    print("\n" + "=" * 50)
    print("📊 RESUMO FINAL:")
    for nome, artigos in data.items():
        if len(artigos) > 0:
            print(f"  ✅ {nome}: {len(artigos)} artigos")
        else:
            print(f"  ❌ {nome}: Falhou ou sem artigos")
    print(f"\n  📈 TOTAL: {total_artigos} artigos coletados")
    print(f"\n⏱️  Tempo total: {tempo_total:.2f}s")
    print("=" * 50)

    return data

def dataclass_asdict(data):
    dataAsDict = {}
    for journal_name, articles in data.items():
        dataAsDict[journal_name] = []
        for article in articles:
            articleDict = asdict(article)
            articleDict["scraped_at"] = articleDict['scraped_at'].isoformat()
            dataAsDict[journal_name].append(articleDict)
    return dataAsDict


FUNCTIONS_MAP = {
    "O povo": {"func": fetch_opovo, "urlParameters": JORNAIS_MAP["opovo"]},
    "Diário do Nordeste": {
        "func": fetch_dn,
        "urlParameters": JORNAIS_MAP["dn"],
    },
    "O Estado CE": {
        "func": fetch_oestadoce,
        "urlParameters": JORNAIS_MAP["oestadoce"],
    },
    "Verdes Mares": {
        "func": fetch_verdemares,
        "urlParameters": JORNAIS_MAP["verdemares"],
    },
    "Ceará Agora": {
        "func": fetch_cearaagora,
        "urlParameters": JORNAIS_MAP["cearaagora"],
    },
    "Tribunal de Contas do Ceará": {
        "func": fetch_tce,
        "urlParameters": JORNAIS_MAP["tce"],
    },
    "Terra da Luz": {
        "func": fetch_terra_da_luz,
        "urlParameters": JORNAIS_MAP["terra_da_luz"],
    },
    "Jornal Jangadeiro": {
        "func": fetch_jangadeiro,
        "urlParameters": JORNAIS_MAP["jangadeiro"],
    },
}
