from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import clear_html_string, creation_time


async def fetch_terra_da_luz(session, url, params, headers):
    articles: list[Article] = []

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
                        Article(
                            title=titulo,
                            subtitle=subtitulo,
                            category=None,
                            author=None,
                            publicationDate=item["date"],
                            link=item["link"],
                            journal="portalterradaluz",
                            createdAt=creation_time(),
                        )
                    )
                except KeyError as e:
                    print(f"Erro no item: {item}")
                    print(f"Erro: {e}")
        except KeyError as e:
            print(f"Erro no fetch dos dados terra da luz: {e}")

    return articles
