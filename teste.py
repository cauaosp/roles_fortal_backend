import asyncio
import html
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup
from utils.const import JORNAIS_MAP
from utils.functions import FUNCTIONS_MAP


async def scraping_limitado(sem, nome: str, config: Dict[str, Any]):
    async with sem:
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Iniciando: {nome}")
        try:
            func = config["func"]
            params = config["params"]

            # Adapta conforme a estrutura dos parâmetros
            if "params" in params and "headers" in params:
                # Para funções que esperam (url, params, headers)
                resultado = await func(
                    params["url"], params.get("params", {}), params["headers"]
                )
            elif "headers" in params:
                # Para funções que esperam (url, headers)
                resultado = await func(params["url"], params["headers"])
            else:
                # Para funções que esperam apenas url
                resultado = await func(params["url"])

            print(
                f"[{time.strftime('%H:%M:%S')}] ✅ Finalizado: {nome} - {len(resultado)} artigos"
            )
            return nome, resultado
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Erro em {nome}: {e}")
            import traceback

            traceback.print_exc()
            return nome, []


async def fetch_concurrent(limit: int = 4):
    data = {nome: [] for nome in FUNCTIONS_MAP.keys()}

    sem = asyncio.Semaphore(limit)

    tarefas = [
        scraping_limitado(sem, nome, config) for nome, config in FUNCTIONS_MAP.items()
    ]

    resultados = await asyncio.gather(*tarefas)

    # Preencher o dicionário com os resultados
    for nome, artigos in resultados:
        data[nome].extend(artigos)

    # Estatísticas finais
    total_artigos = sum(len(artigos) for artigos in data.values())
    print("\n" + "=" * 50)
    print("📊 RESUMO FINAL:")
    for nome, artigos in data.items():
        if len(artigos) > 0:
            print(f"  ✅ {nome}: {len(artigos)} artigos")
        else:
            print(f"  ❌ {nome}: Falhou ou sem artigos")
    print(f"\n  📈 TOTAL: {total_artigos} artigos coletados")
    print("=" * 50)

    return data


async def main():
    resultados_total = await fetch_concurrent()  # 4 scraping simultâneos

    # Acessar resultados
    print(f"O Povo: {len(resultados_total['opovo'])} artigos")
    print(f"Diário do Nordeste: {len(resultados_total['dn'])} artigos")

    return resultados_total


if __name__ == "__main__":
    asyncio.run(main())
