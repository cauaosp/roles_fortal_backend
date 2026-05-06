import json
import time
from datetime import datetime, timedelta, timezone

import requests


def creation_time():
    fuso_brasilia = timezone(timedelta(hours=-3))
    return datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")


def fetch_opovo(url, params, headers):
    opovo_articles = []

    for i in range(3):
        params["offset"] = i * 30

        try:
            response = requests.get(url, params=params, headers=headers)
            print(response.status_code, "opovo")
            data = response.json()

            created_at = creation_time()
            for item in data:
                try:
                    opovo_articles.append(
                        {
                            "titulo": item["ds_matia_titlo"],
                            "subtitulo": item["ds_matia_chape"] or None,
                            "categoria": item["ds_site"],
                            "autor": item["nm_autor"],
                            "dataPublicacao": item["dt_matia_publi"],
                            "link": "https://www.opovo.com.br" + item["ds_matia_path"],
                            "jornal": "opovo",
                            "createdAt": created_at,
                        }
                    )
                except KeyError:
                    print("Erro ao processar item:", item)
                    continue
        except KeyError:
            print("Erro no fetch dos dados")
            continue

    return opovo_articles


def fetch_gcmais(url, params, headers):
    gcmais_articles = []

    try:
        response = requests.get(url, params=params, headers=headers)
        print(response.status_code, "gcmais")
        data = response.json()

        created_at = creation_time()

        for item in data:
            try:
                categorias = (
                    item.get("yoast_head_json", {})
                    .get("schema", {})
                    .get("@graph", [{}])[0]
                    .get("articleSection", [])
                )

                gcmais_articles.append(
                    {
                        "titulo": item["title"]["rendered"],
                        "subtitulo": item.get("acf", {}).get("post_gravata"),
                        "categoria": categorias,
                        "autor": item.get("yoast_head_json", {}).get("author"),
                        "dataPublicacao": item["date"],
                        "link": item["link"],
                        "jornal": "gcmais",
                        "createdAt": created_at,
                    }
                )
            except KeyError:
                print("Erro ao processar item:", item)
                continue
    except KeyError:
        print("Erro no fetch dos dados")

    return gcmais_articles


if __name__ == "__main__":
    jornais = {
        "opovo": {
            "url": "https://www.opovo.com.br/index.php",
            "params": {
                "id": "/reboot/src/endpoints/VerMais.php",
                "dinamico": 1,
                "site_arvor": "Vida&Arte",
                "offset": 0,
                "limit": 30,
            },
            "headers": {"User-Agent": "Mozilla/5.0"},
        },
        "gcmais": {
            "url": "https://gcmais.com.br/wp-json/wp/v2/posts",
            "params": {
                "categories": "1",
                "page": "1",
                "per_page": "90",
            },
            "headers": {"User-Agent": "Mozilla/5.0"},
        },
    }

    n = 0

    while n == 0:
        data = {
            "opovo": [],
            "gcmais": [],
            "diarionordeste": [],
            "g1": [],
            "cearaagora": [],
            "tribunadoceara": [],
            "portalterraluz": [],
            "noticiasceara": [],
            "jornaldobrasil": [],
        }
        data["opovo"].extend(
            fetch_opovo(
                jornais["opovo"]["url"],
                jornais["opovo"]["params"],
                jornais["opovo"]["headers"],
            )
        )
        data["gcmais"].extend(
            fetch_gcmais(
                jornais["gcmais"]["url"],
                jornais["gcmais"]["params"],
                jornais["gcmais"]["headers"],
            )
        )

        with open("data/artigos_ceara.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"total: {sum(len(v) for v in data.values())} artigos")

        counts = {k: len(v) for k, v in data.items()}
        print(counts)
        n += 1

        # time.sleep(360)
