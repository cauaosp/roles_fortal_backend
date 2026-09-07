from models.articles import Article
from utils.helpers import clear_html_string, creation_time, normalize_publication_date


async def fetch_opovo(session, url, params, headers):
    opovo_articles: list[Article] = []

    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para opovo")
                return opovo_articles

            data = await response.json()

            createdAt = creation_time()

            for item in data:
                try:
                    publication_date_normalized = normalize_publication_date(item["dt_matia_publi"])
                    opovo_articles.append(
                        Article(
                            title=item["ds_matia_titlo"],
                            subtitle=str(clear_html_string(item["ds_matia_chape"])),
                            category=item["ds_site"],
                            author=item["nm_autor"],
                            publication_date=publication_date_normalized,
                            link="https://www.opovo.com.br" + item["ds_matia_path"],
                            journal="opovo",
                            scraped_at=createdAt,
                        )
                    )
                except KeyError:
                    print("Erro ao processar item:", item)
                    continue
    except KeyError as e:
        print(f"Erro ao buscar item: {e}")

    return opovo_articles
