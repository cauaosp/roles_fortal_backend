import asyncio
import html
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import aiohttp
import requests
from bs4 import BeautifulSoup
from utils.const import JORNAIS_MAP


def creation_time():
    fuso_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")


async def fetch_opovo(url, params, headers):
    opovo_articles = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"Erro HTTP {response.status} para opovo")
                    return opovo_articles

                print(response.status, "opovo")

                data = await response.json()

                created_at = creation_time()

                for item in data:
                    try:
                        opovo_articles.append(
                            {
                                "titulo": item["ds_matia_titlo"],
                                "subtitulo": item["ds_matia_chape"] or None,
                                "categoria": item["ds_site"],
                                "autor": item["nm_autor"],
                                "dataPublicacao": item["dt_matia_publi"],
                                "link": "https://www.opovo.com.br"
                                + item["ds_matia_path"],
                                "jornal": "opovo",
                                "createdAt": created_at,
                            }
                        )
                    except KeyError:
                        print("Erro ao processar item:", item)
                        continue
        except Exception as e:
            print(f"Erro ao buscar opovo: {e}")

    return opovo_articles


async def fetch_dn(url, headers):
    dn_articles = []

    async with aiohttp.ClientSession() as session:
        try:
            for i in range(3):
                try:
                    url_paged = url + f"?page={i + 1}"
                    async with session.get(url_paged, headers=headers) as response:
                        if response.status != 200:
                            print(f"Erro HTTP {response.status} para opovo")
                            return dn_articles

                        print(response.status, "diario do nordeste")

                        html = await response.text()

                        soup = BeautifulSoup(html, "html.parser")

                        jsonld_script = soup.find(
                            "script", {"type": "application/ld+json"}
                        )

                        if not jsonld_script or jsonld_script.string is None:
                            return dn_articles

                        data = json.loads(jsonld_script.string)

                        if "@graph" in data and len(data["@graph"]) > 0:
                            collection_page = data["@graph"][0]

                            if "hasPart" in collection_page:
                                for item in collection_page["hasPart"]:
                                    if item.get("@type") == "NewsArticle":
                                        article = {
                                            "titulo": item.get("headline", ""),
                                            "autor": item.get("author", {}).get(
                                                "name", ""
                                            )
                                            if isinstance(item.get("author"), dict)
                                            else "",
                                            "dataPublicacao": item.get(
                                                "datePublished", ""
                                            ),
                                            "link": item.get("url", ""),
                                            "jornal": "diariodonordeste",
                                            "createdAt": creation_time(),
                                        }
                                        dn_articles.append(article)

                except KeyError:
                    print("Erro no fetch dos dados")
        except Exception as e:
            print(f"Erro ao buscar dn: {e}")

    return dn_articles


async def fetch_oestadoce(url, params, headers):
    oestadoce_articles = []

    try:
        async with aiohttp.ClientSession().get(
            url, params=params, headers=headers
        ) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para o estado")
                return oestadoce_articles

            print(response.status, "o estado")

            data = await response.json()

            created_at = creation_time()

            for item in data:
                try:
                    categorias = (
                        item.get("yoast_head_json", {})
                        .get("schema", {})
                        .get("@graph", [{}])[0]
                        .get("articleSection", [])
                    )

                    oestadoce_articles.append(
                        {
                            "titulo": item["title"]["rendered"],
                            "subtitulo": item.get("acf", {}).get("post_gravata"),
                            "categoria": categorias,
                            "autor": item.get("yoast_head_json", {}).get("author"),
                            "dataPublicacao": item["date"],
                            "link": item["link"],
                            "jornal": "oestadoce",
                            "createdAt": created_at,
                        }
                    )
                except KeyError:
                    print("Erro ao processar item:", item)
                    continue

    except KeyError as e:
        print(f"Erro ao buscar dados do oestadoce {e}")

    return oestadoce_articles


async def fetch_verdemares(url, headers):
    articles = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Erro ao buscar dados do verdemares {response.status}")
                    return articles

                print(response.status, "globoce")

                xml = await response.text()

                soup = BeautifulSoup(xml, "xml")

                items = soup.find_all("item")[:30]

                for item in items:
                    title_tag = item.title
                    titulo = title_tag.get_text() if title_tag else None

                    subtitle_tag = item.find("atom:subtitle")
                    subtitulo = subtitle_tag.get_text() if subtitle_tag else None

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
                            "jornal": "g1ceara",
                            "createdAt": creation_time(),
                        }
                    )
    except KeyError as e:
        print(f"Erro no fetch de dados da verdemares {e}")

    return articles


async def fetch_cearaagora(url, params, headers):
    articles = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"Erro HTTP {response.status} para cearaagora")
                    return articles

                print(response.status, "cearaagora")

                items = await response.json()

                for item in items:
                    author_id = item["author"]
                    categorias_id = item.get("categories", [])
                    categorias = []

                    url_autor = (
                        f"https://cearaagora.com.br/wp-json/wp/v2/users/{author_id}"
                    )
                    autor = requests.get(url_autor, headers=headers).json()

                    for i in range(len(categorias_id)):
                        url_categoria = f"https://cearaagora.com.br/wp-json/wp/v2/categories/{categorias_id[i]}"
                        categoria = requests.get(url_categoria, headers=headers).json()
                        categorias.append(categoria["name"])

                    articles.append(
                        {
                            "titulo": item["title"]["rendered"],
                            "subtitulo": item["excerpt"]["rendered"],
                            "categoria": "",
                            "autor": autor["name"],
                            "dataPublicacao": item["date"],
                            "link": item["link"],
                            "jornal": "cearaagora",
                            "created_at": creation_time(),
                        }
                    )
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")

    return articles


async def fetch_tce(url, params, headers):
    articles = []

    try:
        async with aiohttp.ClientSession() as session:
            for i in range(3):
                params["start"] = i * 11
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        print(f"Erro na requisição: {response.status}")
                        continue

                    print(response.status, "tce")

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

                                subtitulo = soup_summary.get_text(" ", strip=True)[:150]

                            category_tag = item.find("category")
                            categoria = (
                                category_tag.get("term") if category_tag else None
                            )

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

                            jornal = "Tribunal de Contas do Ceará"

                            createdAt = creation_time()

                            articles.append(
                                {
                                    "titulo": titulo,
                                    "subtitulo": subtitulo,
                                    "categoria": categoria,
                                    "autor": autor,
                                    "dataPublicacao": dataPublicacao,
                                    "link": link,
                                    "jornal": jornal,
                                    "createdAt": createdAt,
                                }
                            )
                        except Exception:
                            print(f"Erro no item: {item}")
                            continue
    except KeyError as e:
        print(f"Erro no fetch dos dados do tce: {e}")

    return articles


async def fetch_terra_da_luz(url, params, headers):
    articles = []

    try:
        async with aiohttp.ClientSession() as session:
            post_task = session.get(url, params=params, headers=headers)

            users_response = session.get(
                    url="https://portalterradaluz.com.br/wp-json/wp/v2/users",
                    headers=headers,
                )

            categories_response = session.get(
                    url="https://portalterradaluz.com.br/wp-json/wp/v2/categories",
                    headers=headers,
                )

            users_data = users_response.json()

            items = await post_task.json()


            authors_map = {user["id"]: user["name"] for user in users_data}

            categories_data = categories_response.json()

            categories_map = {
                category["id"]: category["name"] for category in categories_data
            }



                for item in items:
                    try:
                        categories = []
                        categories_list = item["categories"]
                        for category_id in categories_list:
                            categories.append(categories_map.get(category_id))

                        author_id = item["author"]
                        author_name = authors_map.get(author_id)

                        titulo_html = item["title"]["rendered"]
                        excerpt_html = item["excerpt"]["rendered"]

                        titulo = BeautifulSoup(titulo_html, "html.parser").get_text(
                            " ", strip=True
                        )

                        subtitulo = BeautifulSoup(excerpt_html, "html.parser").get_text(
                            " ", strip=True
                        )

                        articles.append(
                            {
                                "titulo": titulo,
                                "subtitulo": subtitulo,
                                "categoria": categories,
                                "autor": author_name,
                                "dataPublicacao": item["date"],
                                "link": item["link"],
                                "jornal": "Portal Terra da Luz",
                                "created_at": creation_time(),
                            }
                        )
                    except KeyError:
                        print(f"Erro no item: {item}")
    except KeyError as e:
        print(f"Erro no fetch dos dados terra da luz: {e}")

    return articles


# async def fetch_secult(url, params, headers):
#     articles = []

#     try:
#         response = requests.get(
#             url,
#             params=params,
#             headers=headers,
#         )

#         print(response.status_code, "secult")

#         if response.status_code != 200:
#             print(f"Erro HTTP {response.status_code} para secult")
#             return articles

#         items = response.json()

#         for item in items:
#             titulo = item["title"]["rendered"]

#             subtitulo_puro = item["excerpt"]["rendered"]
#             subtitulo = BeautifulSoup(subtitulo_puro, "html.parser").get_text(
#                 " ", strip=True
#             )

#             categorias = []

#             if "_embedded" in item and "wp:term" in item["_embedded"]:
#                 termos = item["_embedded"]["wp:term"]
#                 for taxonomia in termos:
#                     if taxonomia and len(taxonomia) > 0:
#                         primeiro_termo = taxonomia[0]
#                         if primeiro_termo.get("taxonomy") == "category":
#                             for cat in taxonomia:
#                                 categorias.append(cat.get("name"))
#                             break

#             autor_nome = None

#             if "yoast_head_json" in item:
#                 autor_nome = item["yoast_head_json"].get("author")

#             dataPublicacao = item["date"]

#             link = item["link"]

#             articles.append(
#                 {
#                     "titulo": titulo,
#                     "subtitulo": subtitulo,
#                     "categoria": categorias,
#                     "autor": autor_nome,
#                     "dataPublicacao": dataPublicacao,
#                     "link": link,
#                     "jornal": "Secult",
#                     "created_at": creation_time(),
#                 }
#             )

#     except KeyError:
#         print("Erro no fetch dos dados")

#     return articles


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


FUNCTIONS_MAP = {
    # "opovo": {"func": fetch_opovo, "params": JORNAIS_MAP["opovo"]},
    # "dn": {
    #     "func": fetch_dn,
    #     "params": JORNAIS_MAP["dn"],
    # },
    # "oestadoce": {
    #     "func": fetch_oestadoce,
    #     "params": JORNAIS_MAP["oestadoce"],
    # },
    # "verdemares": {
    #     "func": fetch_verdemares,
    #     "params": JORNAIS_MAP["verdemares"],
    # },
    # "cearaagora": {
    #     "func": fetch_cearaagora,
    #     "params": JORNAIS_MAP["cearaagora"],
    # },
    # "terra_da_luz": {
    #     "func": fetch_terra_da_luz,
    #     "params": JORNAIS_MAP["terra_da_luz"],
    # },
    "tce": {
        "func": fetch_tce,
        "params": JORNAIS_MAP["tce"],
    },
    # "secult": {
    #     "func": fetch_secult,
    #     "params": JORNAIS_MAP["secult"],
    # },
}
