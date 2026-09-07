from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import clear_html_string, creation_time, normalize_publication_date


async def fetch_terra_da_luz(session, url, params, headers):
    articles: list[Article] = []

    async with session.get(url, params=params, headers=headers) as response:
        try:
            items = await response.json()

            scraped_at = creation_time()

            for item in items:
                try:

                    titulo_html = item["title"]["rendered"]
                    excerpt_html = item["excerpt"]["rendered"]

                    title = BeautifulSoup(titulo_html, "html.parser").get_text(
                        " ", strip=True
                    )

                    subtitle = clear_html_string(
                        BeautifulSoup(excerpt_html, "html.parser").get_text(" ", strip=True)
                    )

                    publication_date = normalize_publication_date(item["date"])

                    articles.append(
                        Article(
                            title=title,
                            subtitle=subtitle,
                            category=None,
                            author=None,
                            publication_date=publication_date,
                            link=item["link"],
                            journal="portalterradaluz",
                            scraped_at=scraped_at,
                        )
                    )
                except KeyError as e:
                    print(f"Erro no item: {item}")
                    print(f"Erro: {e}")
        except KeyError as e:
            print(f"Erro no fetch dos dados terra da luz: {e}")

    return articles
