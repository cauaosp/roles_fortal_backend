import asyncio
import html
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import aiohttp
import requests
from bs4 import BeautifulSoup
from utils.const import JORNAIS_MAP


def creation_time():
    fuso_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")


async def fetch_opovo(session, url, params, headers):
    opovo_articles = []

    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para opovo")
                return opovo_articles

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
                            "link": "https://www.opovo.com.br" + item["ds_matia_path"],
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


async def fetch_dn(session, url, headers):
    dn_articles = []

    try:
        for i in range(3):
            try:
                url_paged = url + f"?page={i + 1}"
                async with session.get(url_paged, headers=headers) as response:
                    if response.status != 200:
                        print(f"Erro HTTP {response.status} para opovo")
                        return dn_articles

                    html = await response.text()

                    soup = BeautifulSoup(html, "html.parser")

                    jsonld_script = soup.find("script", {"type": "application/ld+json"})

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
                                        "autor": item.get("author", {}).get("name", "")
                                        if isinstance(item.get("author"), dict)
                                        else "",
                                        "dataPublicacao": item.get("datePublished", ""),
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


async def fetch_oestadoce(session, url, params, headers):
    oestadoce_articles = []

    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para o estado")
                return oestadoce_articles

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


async def fetch_cearaagora(session, url, params, headers):
    articles = []

    try:
        fetch_posts = session.get(url, params=params, headers=headers)

        url_autor = "https://cearaagora.com.br/wp-json/wp/v2/users/"
        fetch_author = session.get(url_autor, headers=headers)

        url_categoria = "https://cearaagora.com.br/wp-json/wp/v2/categories/"
        fetch_categories = session.get(url_categoria, headers=headers)

        fetch_posts, fetch_author, fetch_categories = await asyncio.gather(
            fetch_posts, fetch_author, fetch_categories
        )

        users_data = await fetch_author.json()
        users_map = {user["id"]: user for user in users_data}

        categories_data = await fetch_categories.json()
        categories_map = {category["id"]: category for category in categories_data}

        items = await fetch_posts.json()

        if fetch_posts.status != 200:
            print(f"Erro HTTP {fetch_posts.status} para cearaagora")
            return articles

        for item in items:
            try:
                categories = []
                categorias_id_list = item.get("categories", [])
                for id in categorias_id_list:
                    categories.append(categories_map.get(id))

                author_id = item.get("author", 0)
                author_obj = users_map.get(author_id)
                author_name = author_obj.get("name", "") if author_obj else ""

                articles.append(
                    {
                        "titulo": item["title"]["rendered"],
                        "subtitulo": item["excerpt"]["rendered"],
                        "categoria": "",
                        "autor": author_name,
                        "dataPublicacao": item["date"],
                        "link": item["link"],
                        "jornal": "cearaagora",
                        "created_at": creation_time(),
                    }
                )
            except KeyError:
                print(f"Erro no item: {item}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")

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
                    print(f"Erro na requisição: {response.status}")
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

                            subtitulo = soup_summary.get_text(" ", strip=True)[:150]

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


async def fetch_terra_da_luz(session, url, params, headers):
    articles = []

    try:
        post_task = session.get(url, params=params, headers=headers)

        users_response = session.get(
            url="https://portalterradaluz.com.br/wp-json/wp/v2/users",
            headers=headers,
        )

        categories_response = session.get(
            url="https://portalterradaluz.com.br/wp-json/wp/v2/categories",
            headers=headers,
        )

        post_task, users_response, categories_response = await asyncio.gather(
            post_task,
            users_response,
            categories_response,
        )

        users_data = await users_response.json()

        authors_map = {user["id"]: user["name"] for user in users_data}

        categories_data = await categories_response.json()

        categories_map = {
            category["id"]: category["name"] for category in categories_data
        }

        items = await post_task.json()

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


async def fetch_secult(session, url, params, headers):
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

            items = await response.json()

            for item in items:
                titulo = item["title"]["rendered"]

                subtitulo_puro = item["excerpt"]["rendered"]
                subtitulo = BeautifulSoup(subtitulo_puro, "html.parser").get_text(
                    " ", strip=True
                )

                categorias = []

                if "_embedded" in item and "wp:term" in item["_embedded"]:
                    termos = item["_embedded"]["wp:term"]
                    for taxonomia in termos:
                        if taxonomia and len(taxonomia) > 0:
                            primeiro_termo = taxonomia[0]
                            if primeiro_termo.get("taxonomy") == "category":
                                for cat in taxonomia:
                                    categorias.append(cat.get("name"))
                                break

                autor_nome = None

                if "yoast_head_json" in item:
                    autor_nome = item["yoast_head_json"].get("author")

                dataPublicacao = item["date"]

                link = item["link"]

                articles.append(
                    {
                        "titulo": titulo,
                        "subtitulo": subtitulo,
                        "categoria": categorias,
                        "autor": autor_nome,
                        "dataPublicacao": dataPublicacao,
                        "link": link,
                        "jornal": "Secult",
                        "created_at": creation_time(),
                    }
                )
    except KeyError:
        print("Erro no fetch dos dados")

    return articles


async def scraping_limitado(session, sem, nome: str, config: Dict[str, Any]):
    async with sem:
        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Iniciando: {nome}")
        try:
            func = config["func"]
            params = config["params"]

            if "params" in params and "headers" in params:
                resultado = await func(
                    session, params["url"], params.get("params", {}), params["headers"]
                )
            elif "headers" in params:
                resultado = await func(session, params["url"], params["headers"])
            else:
                resultado = await func(session, params["url"])

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
    "O povo": {"func": fetch_opovo, "params": JORNAIS_MAP["opovo"]},
    "Diário do Nordeste": {
        "func": fetch_dn,
        "params": JORNAIS_MAP["dn"],
    },
    "O Estado CE": {
        "func": fetch_oestadoce,
        "params": JORNAIS_MAP["oestadoce"],
    },
    "Verdes Mares": {
        "func": fetch_verdemares,
        "params": JORNAIS_MAP["verdemares"],
    },
    "Ceará Agora": {
        "func": fetch_cearaagora,
        "params": JORNAIS_MAP["cearaagora"],
    },
    "Terra da Luz": {
        "func": fetch_terra_da_luz,
        "params": JORNAIS_MAP["terra_da_luz"],
    },
    "Tribunal de Contas do Ceará": {
        "func": fetch_tce,
        "params": JORNAIS_MAP["tce"],
    },
    "Secretaria de Cultura do Ceará": {
        "func": fetch_secult,
        "params": JORNAIS_MAP["secult"],
    },
}
