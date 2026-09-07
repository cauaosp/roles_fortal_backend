from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import (
    clear_html_string,
    creation_time,
    log_html,
    normalize_publication_date,
)


async def fetch_oestadoce(session, url, headers):
    articles: list[Article] = []

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
                        publication_date_normalized = normalize_publication_date(data_publicacao)

                        articles.append(
                            Article(
                                title=titulo,
                                subtitle=subtitulo,
                                category=categoria,
                                author=autor,
                                publication_date=publication_date_normalized,
                                link=link,
                                journal="oestadoce",
                                scraped_at=created_at
                            )
                        )

                        if len(articles) >= 30:
                            return articles

                    except KeyError as e:
                        print("error no item do estadoce: ", e)

    except KeyError as e:
        print(f"Erro no scraper do O Estado CE: {e}")

    return articles
