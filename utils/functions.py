import asyncio
import html
import json
import re
import time
from datetime import datetime, timedelta, timezone
from math import e
from typing import Any, Dict

import aiohttp
import requests
from bs4 import BeautifulSoup
from utils.const import JORNAIS_MAP

def creation_time():
    fuso_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")

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

async def fetch_opovo(session, url, params, headers):
    opovo_articles = []

    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para opovo")
                return opovo_articles

            data = await response.json()

            createdAt = creation_time()

            for item in data:
                try:
                    opovo_articles.append(
                        {
                            "titulo": item["ds_matia_titlo"],
                            "subtitulo": clear_html_string(item["ds_matia_chape"]),
                            "categoria": item["ds_site"],
                            "autor": item["nm_autor"],
                            "dataPublicacao": item["dt_matia_publi"],
                            "link": "https://www.opovo.com.br" + item["ds_matia_path"],
                            "jornal": "opovo",
                            "createdAt": createdAt,
                        }
                    )
                except KeyError:
                    print("Erro ao processar item:", item)
                    continue
    except Exception as e:
        print(f"Erro ao buscar opovo: {e}")

    return opovo_articles

async def fetch_dn(session, url, headers):
    dn_articles = []

    for i in range(3):
        url_paged = url + f"?page={i + 1}"

        try:
            async with session.get(url_paged, headers=headers) as response:
                if response.status != 200:
                    print(f"Erro HTTP {response.status} para Diario do Nordeste")
                    return dn_articles

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                script = soup.find("script", type="application/ld+json")
                artigos_json = {}

                if script and script.string:
                    dados = json.loads(script.string)

                    for item in dados.get("@graph", []):
                        if item.get("@type") != "CollectionPage":
                            continue

                        for noticia in item.get("hasPart", []):
                            artigos_json[noticia["url"]] = noticia

                artigos = [h2.find_parent("div") for h2 in soup.find_all("h2")]

                if not artigos:
                    print("Nenhum artigo encontrado!")
                    return dn_articles

                for artigo in artigos:
                    if len(dn_articles) >= 30:
                        break

                    try:
                        titulo_tag = artigo.find("h2")
                        if not titulo_tag:
                            continue

                        titulo = titulo_tag.get_text(" ", strip=True)

                        link_tag = titulo_tag.find_parent("a", href=True)
                        link = link_tag["href"] if link_tag else None

                        dados_artigo = artigos_json.get(link, {})

                        autor = (
                            dados_artigo.get("author", {}).get("name")
                            if dados_artigo.get("author")
                            else None
                        )

                        data_publicacao = dados_artigo.get("datePublished")

                        links = artigo.find_all("a", href=True)

                        categoria = None
                        subtitulo = None

                        if len(links) >= 2:
                            categoria = links[0].get_text(" ", strip=True)

                        if len(links) >= 3:
                            subtitulo = clear_html_string(
                                links[2].get_text(" ", strip=True)
                            )

                        dn_articles.append(
                            {
                                "titulo": titulo,
                                "subtitulo": subtitulo,
                                "categoria": categoria,
                                "autor": autor,
                                "dataPublicacao": data_publicacao,
                                "link": link,
                                "jornal": "diariodonordeste",
                                "createdAt": creation_time(),
                            }
                        )

                    except Exception as e:
                        print(f"Erro ao processar artigo do Diario do Nordeste: {e}")

        except Exception as e:
            print(f"Erro no fetch dos dados do Diario do Nordeste: {e}")

    return dn_articles

async def fetch_oestadoce(session, url, headers):
    articles = []

    try:
        created_at = creation_time()

        for page in range(1, 4):

            page_url = (
                "https://oestadoce.com.br/category/geral/"
                if page == 1
                else f"https://oestadoce.com.br/category/geral/page/{page}/"
            )

            async with session.get(page_url, headers=headers) as response:
                await log_html(response, "CEARÁ AGORA")

                if response.status != 200:
                    print(f"Erro HTTP {response.status} para O Estado CE")
                    continue

                html = await response.text()

                soup = BeautifulSoup(html, "html.parser")

                noticias = soup.select(
                    ".td_module_wrap, .tdb_module_loop, .td_module_flex"
                )

                for noticia in noticias:

                    try:

                        titulo_tag = noticia.select_one("h3.entry-title a")

                        if not titulo_tag:
                            continue

                        titulo = titulo_tag.get_text(" ", strip=True)

                        link = titulo_tag["href"]

                        resumo_tag = noticia.select_one(".td-excerpt")

                        subtitulo = (
                            clear_html_string(
                                resumo_tag.get_text(" ", strip=True)
                            )
                            if resumo_tag
                            else None
                        )

                        categoria_tag = noticia.select_one("a.td-post-category")

                        categoria = (
                            categoria_tag.get_text(strip=True)
                            if categoria_tag
                            else None
                        )

                        autor = None

                        autor_img = noticia.select_one(".tdb-author-photo img")

                        if autor_img:
                            autor = autor_img.get("alt")

                        data_tag = noticia.select_one("time.entry-date")

                        data_publicacao = (
                            data_tag.get("datetime")
                            if data_tag
                            else None
                        )

                        articles.append(
                            {
                                "titulo": titulo,
                                "subtitulo": subtitulo,
                                "categoria": categoria,
                                "autor": autor,
                                "dataPublicacao": data_publicacao,
                                "link": link,
                                "jornal": "oestadoce",
                                "createdAt": created_at,
                            }
                        )

                        if len(articles) >= 30:
                            return articles

                    except Exception as e:
                        print(e)
                        continue

    except Exception as e:
        print(f"Erro no scraper do O Estado CE: {e}")

    return articles

async def fetch_verdemares(session, url, headers):
    articles = []

    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Erro ao buscar dados do verdemares {response.status}")
                return articles

            xml = await response.text()

            soup = BeautifulSoup(xml, "xml")

            items = soup.find_all("item")[:30]

            for item in items:
                title_tag = item.title
                titulo = title_tag.get_text() if title_tag else None

                subtitle_tag = item.find("atom:subtitle")
                subtitulo = clear_html_string(subtitle_tag.get_text())

                link_tag = item.link
                link = link_tag.get_text() if link_tag else None

                pubdate_tag = item.pubDate
                data = pubdate_tag.get_text() if pubdate_tag else None

                category_tag = item.category
                categoria = category_tag.get_text() if category_tag else None

                articles.append(
                    {
                        "titulo": titulo,
                        "subtitulo": subtitulo,
                        "categoria": categoria,
                        "dataPublicacao": data,
                        "link": link,
                        "jornal": "verdesmares",
                        "createdAt": creation_time(),
                    }
                )
    except KeyError as e:
        print(f"Erro no fetch de dados da verdemares {e}")

    return articles

async def fetch_cearaagora(session, url, params, headers):
    articles = []

    try:
        async with session.get(url, params=params, headers=headers) as response:
            await log_html(response, "CEARÁ AGORA")

            if response.status != 200:
                print(f"Erro HTTP {response.status} para o cearaagora")
                print(f"Error: {response.text}")
                return articles

            data = await response.json()

            createdAt = creation_time()

            for item in data:
                try:
                    subtitle = clear_html_string(item["excerpt"]["rendered"])

                    articles.append(
                        {
                            "titulo": item["title"]["rendered"],
                            "subtitulo": subtitle,
                            "categoria": None,
                            "autor": None,
                            "dataPublicacao": item["date"],
                            "link": item["link"],
                            "jornal": "cearaagora",
                            "createdAt": createdAt,
                        }
                    )
                except KeyError:
                    print(f"Erro no item: {item}")
    except requests.exceptions.RequestException as e:
        print(f"Erro no fetch do Ceará Agora: {e}")

    return articles

async def fetch_tce(session, url, params, headers):
    articles = []

    try:
        for i in range(3):
            params["start"] = i * 11
            async with session.get(
                url,
                params=params,
                headers=headers,
            ) as response:
                if response.status != 200:
                    print(f"Erro {response.status} na requisição do TCE!")
                    continue

                xml_response = await response.text()

                soup = BeautifulSoup(xml_response, "xml")

                items = soup.find_all("entry")

                subtitulo = None

                for item in items:
                    try:
                        titulo_tag = item.title
                        titulo = titulo_tag.get_text() if titulo_tag else None

                        sumario_tag = item.find("summary")
                        sumario = sumario_tag.get_text() if sumario_tag else None

                        if sumario:
                            decoded = html.unescape(sumario)

                            soup_summary = BeautifulSoup(decoded, "html.parser")

                            for img in soup_summary.find_all("img"):
                                img.decompose()

                            subtitulo = clear_html_string(
                                soup_summary.get_text(" ", strip=True)
                            )

                        category_tag = item.find("category")
                        categoria = category_tag.get("term") if category_tag else None

                        author_tag = item.find("author")
                        author_name_tag = (
                            author_tag.find("name") if author_tag else None
                        )
                        autor = (
                            author_name_tag.get_text().strip()
                            if author_name_tag
                            else None
                        )

                        date_tag = item.published
                        dataPublicacao = date_tag.get_text() if date_tag else None

                        link_tag = item.id
                        link = link_tag.get_text() if link_tag else None

                        createdAt = creation_time()

                        articles.append(
                            {
                                "titulo": titulo,
                                "subtitulo": subtitulo,
                                "categoria": categoria,
                                "autor": autor,
                                "dataPublicacao": dataPublicacao,
                                "link": link,
                                "jornal": "tce",
                                "createdAt": createdAt,
                            }
                        )
                    except Exception:
                        print(f"Erro no item: {item}")
                        continue
    except KeyError as e:
        print(f"Erro no fetch dos dados do tce: {e}")

    return articles

async def fetch_terra_da_luz(session, url, params, headers):
    articles = []

    async with session.get(url, params=params, headers=headers) as response:
        try:
            items = await response.json()

            for item in items:
                try:

                    titulo_html = item["title"]["rendered"]
                    excerpt_html = item["excerpt"]["rendered"]

                    titulo = BeautifulSoup(titulo_html, "html.parser").get_text(
                        " ", strip=True
                    )

                    subtitulo = clear_html_string(
                        BeautifulSoup(excerpt_html, "html.parser").get_text(" ", strip=True)
                    )

                    articles.append(
                        {
                            "titulo": titulo,
                            "subtitulo": subtitulo,
                            "categoria": None,
                            "autor": None,
                            "dataPublicacao": item["date"],
                            "link": item["link"],
                            "jornal": "portalterradaluz",
                            "createdAt": creation_time(),
                        }
                    )
                except KeyError:
                    print(f"Erro no item: {item}")
        except KeyError as e:
            print(f"Erro no fetch dos dados terra da luz: {e}")

    return articles

async def fetch_jangadeiro(session, url, params, headers):
    articles = []

    try:
        async with session.get(
            url,
            params=params,
            headers=headers,
        ) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para secult")
                return articles

            data = await response.json()

            createdAt = creation_time()

            for item in data:
                try:
                    subtitulo = clear_html_string(item["excerpt"]["rendered"])

                    articles.append(
                        {
                            "titulo": item["title"]["rendered"],
                            "subtitulo": subtitulo,
                            "categoria": None,
                            "autor": None,
                            "dataPublicacao": item["date"],
                            "link": item["link"],
                            "jornal": "jangadeiro",
                            "createdAt": createdAt,
                        }
                    )
                except KeyError as e:
                    print("Erro no processamento do item: ", e)
    except KeyError:
        print("Erro no fetch dos dados")

    return articles

async def scraping_limitado(session, sem, nome: str, config: Dict[str, Any]):
    async with sem:
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
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Erro em {nome}: {e}")
            import traceback

            traceback.print_exc()
            return nome, []

async def fetch_concurrent(limit: int = 4):
    data = {nome: [] for nome in FUNCTIONS_MAP.keys()}

    sem = asyncio.Semaphore(limit)

    inicio = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tarefas = [
            scraping_limitado(session, sem, nome, config)
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
    "Terra da Luz": {
        "func": fetch_terra_da_luz,
        "urlParameters": JORNAIS_MAP["terra_da_luz"],
    },
    "Tribunal de Contas do Ceará": {
        "func": fetch_tce,
        "urlParameters": JORNAIS_MAP["tce"],
    },
    "Jornal Jangadeiro": {
        "func": fetch_jangadeiro,
        "urlParameters": JORNAIS_MAP["jangadeiro"],
    },
}
