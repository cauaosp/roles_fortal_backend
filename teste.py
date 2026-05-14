import html
import json

import requests
from bs4 import BeautifulSoup
from utils.functions import creation_time


def fetch_secult(url, params, headers):
    articles = []

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
        )

        print(response.status_code, "secult")

        items = response.json()

        for item in items:
            titulo = item["title"]["rendered"]

            subtitulo_puro = item["excerpt"]["rendered"]
            subtitulo = BeautifulSoup(subtitulo_puro, "html.parser").get_text(
                " ", strip=True
            )

            categorias = []

            if "_embedded" in item and "wp:term" in item["_embedded"]:
                termos = item["_embedded"]["wp:term"]
                for taxonomia in termos:
                    if taxonomia and len(taxonomia) > 0:
                        primeiro_termo = taxonomia[0]
                        if primeiro_termo.get("taxonomy") == "category":
                            for cat in taxonomia:
                                categorias.append(cat.get("name"))
                            break

            autor_nome = None

            if "yoast_head_json" in item:
                autor_nome = item["yoast_head_json"].get("author")

            dataPublicacao = item["date"]

            link = item["link"]

            articles.append(
                {
                    "titulo": titulo,
                    "subtitulo": subtitulo,
                    "categoria": categorias,
                    "autor": autor_nome,
                    "dataPublicacao": dataPublicacao,
                    "link": link,
                    "jornal": "Secult",
                    "created_at": creation_time(),
                }
            )

    except KeyError:
        print("Erro no fetch dos dados")

    return articles


if __name__ == "__main__":
    jornal = {
        "secult": {
            "url": "https://www.secult.ce.gov.br/wp-json/wp/v2/posts",
            "params": {
                "_embed": "true",
                "per_page": "30",
                "page": "1",
            },
            "headers": {"User-Agent": "Mozilla/5.0"},
        }
    }

    articles_list = fetch_secult(
        jornal["secult"]["url"],
        jornal["secult"]["params"],
        jornal["secult"]["headers"],
    )

    print(f"total: {len(articles_list)} artigos")
    print(f"\n {json.dumps(articles_list[:5], indent=4)}")
