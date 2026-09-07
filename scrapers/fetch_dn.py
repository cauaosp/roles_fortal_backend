import json

from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import clear_html_string, creation_time, normalize_publication_date


async def fetch_dn(session, url, headers):
    dn_articles: list[Article] = []

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

                        autor_data = dados_artigo.get("author")
                        autor = extract_author_name(autor_data)

                        data_publicacao = dados_artigo.get("datePublished")
                        publication_date_normalized = normalize_publication_date(data_publicacao)

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
                            Article(
                                title=titulo,
                                subtitle=subtitulo,
                                category=categoria,
                                author=autor,
                                publication_date=publication_date_normalized,
                                link=link,
                                journal="diariodonordeste",
                                scraped_at=creation_time(),
                            )
                        )

                    except KeyError as e:
                        print(f"Erro ao processar artigo do Diario do Nordeste: {e}")

        except KeyError as e:
            print(f"Erro no fetch dos dados do Diario do Nordeste: {e}")

    return dn_articles


def extract_author_name(author_data):
    """Extrai o nome do autor, seja objeto ou lista"""
    if not author_data:
        return None

    if isinstance(author_data, list):
        if len(author_data) > 0:
            first_author = author_data[0]
            if isinstance(first_author, dict):
                return first_author.get("name")
        return None

    if isinstance(author_data, dict):
        return author_data.get("name")

    if isinstance(author_data, str):
        return author_data

    return None
