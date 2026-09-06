from models.articles import Article
from utils.helpers import clear_html_string, creation_time


async def fetch_jangadeiro(session, url, params, headers):
    articles: list[Article] = []

    try:
        async with session.get(
            url,
            params=params,
            headers=headers,
        ) as response:
            if response.status != 200:
                print(f"Erro HTTP {response.status} para secult")
                return articles

            data = await response.json()

            createdAt = creation_time()

            for item in data:
                try:
                    subtitulo = clear_html_string(item["excerpt"]["rendered"])

                    articles.append(
                        Article(
                            title=item["title"]["rendered"],
                            subtitle=subtitulo,
                            category=None,
                            author=None,
                            publicationDate=item["date"],
                            link=item["link"],
                            journal="jangadeiro",
                            createdAt=createdAt,
                        )
                    )
                except KeyError as e:
                    print("Erro no processamento do item: ", e)
    except KeyError:
        print("Erro no fetch dos dados")

    return articles
