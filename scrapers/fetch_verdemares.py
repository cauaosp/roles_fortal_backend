from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import clear_html_string, creation_time


async def fetch_verdemares(session, url, headers):
    articles: list[Article] = []

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

                if not titulo:
                    print(f"⚠️ Pulando item sem título: {item}")
                    continue

                subtitle_tag = item.find("atom:subtitle")
                subtitulo = clear_html_string(subtitle_tag.get_text())

                link_tag = item.link
                link = link_tag.get_text() if link_tag else None

                pubdate_tag = item.pubDate
                data = pubdate_tag.get_text() if pubdate_tag else None

                category_tag = item.category
                categoria = category_tag.get_text() if category_tag else None

                articles.append(
                    Article(
                        title=titulo,
                        subtitle=subtitulo,
                        category=categoria,
                        author=None,
                        publication_date=data,
                        link=link,
                        journal="verdesmares",
                        scraped_at=creation_time(),
                    )
                )
    except KeyError as e:
        print(f"Erro no fetch de dados da verdemares {e}")

    return articles
