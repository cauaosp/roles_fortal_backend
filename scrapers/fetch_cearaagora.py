import requests
from models.articles import Article
from utils.helpers import clear_html_string, creation_time, log_html


async def fetch_cearaagora(session, url, params, headers):
    articles: list[Article] = []

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
                        Article(
                            title=item["title"]["rendered"],
                            subtitle=subtitle,
                            category=None,
                            author=None,
                            publication_date=item["date"],
                            link=item["link"],
                            journal="cearaagora",
                            scraped_at=createdAt,
                        )
                    )
                except KeyError as e:
                    print(f"Erro no item: {item}")
                    print(f"Erro: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Erro no fetch do Ceará Agora: {e}")

    return articles
