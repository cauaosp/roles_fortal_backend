import html

from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import clear_html_string, creation_time, normalize_publication_date


async def fetch_tce(session, url, params, headers):
    articles: list[Article] = []

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

                createdAt = creation_time()

                for item in items:
                    try:
                        titulo_tag = item.title
                        titulo = titulo_tag.get_text() if titulo_tag else None

                        if not titulo:
                            continue

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
                        publication_date_normalized = normalize_publication_date(dataPublicacao)

                        link_tag = item.id
                        link = link_tag.get_text() if link_tag else None


                        articles.append(
                            Article(
                                title=titulo,
                                subtitle=subtitulo,
                                category=categoria,
                                author=autor,
                                publication_date=publication_date_normalized,
                                link=link,
                                journal="tce",
                                scraped_at=createdAt,
                            )
                        )
                    except KeyError as e:
                        print(f"Erro no item: {item}")
                        print(f"Erro: {e}")
    except KeyError as e:
        print(f"Erro no fetch dos dados do tce: {e}")

    return articles
