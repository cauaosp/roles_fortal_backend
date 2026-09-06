import json

from bs4 import BeautifulSoup
from models.articles import Article
from utils.helpers import clear_html_string, creation_time


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

                        autor = (
                            dados_artigo.get("author", {}).get("name")
                            if dados_artigo.get("author")
                            else None
                        )

                        data_publicacao = dados_artigo.get("datePublished")

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
                                publicationDate=data_publicacao,
                                link=link,
                                journal="diariodonordeste",
                                createdAt=creation_time(),
                            )
                        )

                    except KeyError as e:
                        print(f"Erro ao processar artigo do Diario do Nordeste: {e}")

        except KeyError as e:
            print(f"Erro no fetch dos dados do Diario do Nordeste: {e}")

    return dn_articles
