import html
import json

import requests
from bs4 import BeautifulSoup
from utils.functions import creation_time


def fetch_terra_da_luz(url, params, headers):
    articles = []

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
        )

        print(response.status_code, "terra da luz")

        items = response.json()

        users_response = requests.get(
            url="https://portalterradaluz.com.br/wp-json/wp/v2/users",
            headers=headers,
        )

        users_data = users_response.json()

        authors_map = {user["id"]: user["name"] for user in users_data}

        categories_response = requests.get(
            url="https://portalterradaluz.com.br/wp-json/wp/v2/categories",
            headers=headers,
        )

        categories_data = categories_response.json()

        categories_map = {
            category["id"]: category["name"] for category in categories_data
        }

        for item in items:
            categories = []
            categories_list = item["categories"]
            for category_id in categories_list:
                categories.append(categories_map.get(category_id))

            author_id = item["author"]
            author_name = authors_map.get(author_id)

            titulo_html = item["title"]["rendered"]
            excerpt_html = item["excerpt"]["rendered"]

            titulo = BeautifulSoup(titulo_html, "html.parser").get_text(" ", strip=True)

            subtitulo = BeautifulSoup(excerpt_html, "html.parser").get_text(
                " ", strip=True
            )

            articles.append(
                {
                    "titulo": titulo,
                    "subtitulo": subtitulo,
                    "categoria": categories,
                    "autor": author_name,
                    "dataPublicacao": item["date"],
                    "link": item["link"],
                    "jornal": "Portal Terra da Luz",
                    "created_at": creation_time(),
                }
            )

    except KeyError:
        print("Erro no fetch dos dados")

    return articles


if __name__ == "__main__":
    jornal = {
        "terra_da_luz": {
            "url": "https://portalterradaluz.com.br/wp-json/wp/v2/posts",
            "params": {"page": "1", "per_page": "30"},
            "headers": {"User-Agent": "Mozilla/5.0"},
        }
    }

    # articles_list = fetch_terra_da_luz(
    #     jornal["terra_da_luz"]["url"],
    #     jornal["terra_da_luz"]["params"],
    #     jornal["terra_da_luz"]["headers"],
    # )

    # print(f"total: {len(articles_list)} artigos")
    print("""    "yoast_head": "\u003c!-- This site is optimized with the Yoast SEO plugin v26.7 - https://yoast.com/wordpress/plugins/seo/ --\u003e\n\u003ctitle\u003eTeatro Carlos Câmara recebe visita guiada da comunidade da Sabiaguaba à exposição “TORÉM – Tear dos Encantados” - Secretaria da Cultura\u003c/title\u003e\n\u003cmeta name=\"robots\" content=\"index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1\" /\u003e\n\u003clink rel=\"canonical\" href=\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\" /\u003e\n\u003cmeta property=\"og:locale\" content=\"pt_BR\" /\u003e\n\u003cmeta property=\"og:type\" content=\"article\" /\u003e\n\u003cmeta property=\"og:title\" content=\"Teatro Carlos Câmara recebe visita guiada da comunidade da Sabiaguaba à exposição “TORÉM – Tear dos Encantados” - Secretaria da Cultura\" /\u003e\n\u003cmeta property=\"og:description\" content=\"A ação integra os programas Para Todas as Plateias e Percursos, promovendo um encontro entre território, memória indígena e acesso à cultura no Centro de Fortaleza O Teatro Carlos Câmara e o Sobrado Dr. José Lourenço realizam, no próximo dia 7 de maio (quinta-feira), às 15h, uma visita guiada especial à exposição “TORÉM – Tear [&hellip;]\" /\u003e\n\u003cmeta property=\"og:url\" content=\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\" /\u003e\n\u003cmeta property=\"og:site_name\" content=\"Secretaria da Cultura\" /\u003e\n\u003cmeta property=\"article:published_time\" content=\"2026-05-06T18:27:48+00:00\" /\u003e\n\u003cmeta property=\"og:image\" content=\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2026/05/IMG_3192.jpeg\" /\u003e\n\t\u003cmeta property=\"og:image:width\" content=\"2364\" /\u003e\n\t\u003cmeta property=\"og:image:height\" content=\"1330\" /\u003e\n\t\u003cmeta property=\"og:image:type\" content=\"image/jpeg\" /\u003e\n\u003cmeta name=\"author\" content=\"secultthaisbezerra\" /\u003e\n\u003cmeta name=\"twitter:card\" content=\"summary_large_image\" /\u003e\n\u003cmeta name=\"twitter:label1\" content=\"Escrito por\" /\u003e\n\t\u003cmeta name=\"twitter:data1\" content=\"secultthaisbezerra\" /\u003e\n\t\u003cmeta name=\"twitter:label2\" content=\"Est. tempo de leitura\" /\u003e\n\t\u003cmeta name=\"twitter:data2\" content=\"5 minutos\" /\u003e\n\u003cscript type=\"application/ld+json\" class=\"yoast-schema-graph\"\u003e{\"@context\":\"https://schema.org\",\"@graph\":[{\"@type\":\"Article\",\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#article\",\"isPartOf\":{\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\"},\"author\":{\"name\":\"secultthaisbezerra\",\"@id\":\"https://www.secult.ce.gov.br/#/schema/person/d7782735322c8d978963f5de52bc3143\"},\"headline\":\"Teatro Carlos Câmara recebe visita guiada da comunidade da Sabiaguaba à exposição “TORÉM – Tear dos Encantados”\",\"datePublished\":\"2026-05-06T18:27:48+00:00\",\"mainEntityOfPage\":{\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\"},\"wordCount\":825,\"publisher\":{\"@id\":\"https://www.secult.ce.gov.br/#organization\"},\"image\":{\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#primaryimage\"},\"thumbnailUrl\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2026/05/IMG_3192.jpeg\",\"keywords\":[\"Teatro Carlos Câmara\"],\"articleSection\":[\"Rece\"],\"inLanguage\":\"pt-BR\"},{\"@type\":\"WebPage\",\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\",\"url\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\",\"name\":\"Teatro Carlos Câmara recebe visita guiada da comunidade da Sabiaguaba à exposição “TORÉM – Tear dos Encantados” - Secretaria da Cultura\",\"isPartOf\":{\"@id\":\"https://www.secult.ce.gov.br/#website\"},\"primaryImageOfPage\":{\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#primaryimage\"},\"image\":{\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#primaryimage\"},\"thumbnailUrl\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2026/05/IMG_3192.jpeg\",\"datePublished\":\"2026-05-06T18:27:48+00:00\",\"breadcrumb\":{\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#breadcrumb\"},\"inLanguage\":\"pt-BR\",\"potentialAction\":[{\"@type\":\"ReadAction\",\"target\":[\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/\"]}]},{\"@type\":\"ImageObject\",\"inLanguage\":\"pt-BR\",\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#primaryimage\",\"url\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2026/05/IMG_3192.jpeg\",\"contentUrl\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2026/05/IMG_3192.jpeg\",\"width\":2364,\"height\":1330},{\"@type\":\"BreadcrumbList\",\"@id\":\"https://www.secult.ce.gov.br/2026/05/06/teatro-carlos-camara-recebe-visita-guiada-da-comunidade-da-sabiaguaba-a-exposicao-torem-tear-dos-encantados/#breadcrumb\",\"itemListElement\":[{\"@type\":\"ListItem\",\"position\":1,\"name\":\"Início\",\"item\":\"https://www.secult.ce.gov.br/\"},{\"@type\":\"ListItem\",\"position\":2,\"name\":\"Teatro Carlos Câmara recebe visita guiada da comunidade da Sabiaguaba à exposição “TORÉM – Tear dos Encantados”\"}]},{\"@type\":\"WebSite\",\"@id\":\"https://www.secult.ce.gov.br/#website\",\"url\":\"https://www.secult.ce.gov.br/\",\"name\":\"Secretaria da Cultura\",\"description\":\"Secretaria da Cultura\",\"publisher\":{\"@id\":\"https://www.secult.ce.gov.br/#organization\"},\"potentialAction\":[{\"@type\":\"SearchAction\",\"target\":{\"@type\":\"EntryPoint\",\"urlTemplate\":\"https://www.secult.ce.gov.br/?s={search_term_string}\"},\"query-input\":{\"@type\":\"PropertyValueSpecification\",\"valueRequired\":true,\"valueName\":\"search_term_string\"}}],\"inLanguage\":\"pt-BR\"},{\"@type\":\"Organization\",\"@id\":\"https://www.secult.ce.gov.br/#organization\",\"name\":\"Secretaria da Cultura\",\"url\":\"https://www.secult.ce.gov.br/\",\"logo\":{\"@type\":\"ImageObject\",\"inLanguage\":\"pt-BR\",\"@id\":\"https://www.secult.ce.gov.br/#/schema/logo/image/\",\"url\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2018/05/secult-clara-3.png\",\"contentUrl\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2018/05/secult-clara-3.png\",\"width\":559,\"height\":106,\"caption\":\"Secretaria da Cultura\"},\"image\":{\"@id\":\"https://www.secult.ce.gov.br/#/schema/logo/image/\"}},{\"@type\":\"Person\",\"@id\":\"https://www.secult.ce.gov.br/#/schema/person/d7782735322c8d978963f5de52bc3143\",\"name\":\"secultthaisbezerra\",\"image\":{\"@type\":\"ImageObject\",\"inLanguage\":\"pt-BR\",\"@id\":\"https://www.secult.ce.gov.br/#/schema/person/image/\",\"url\":\"https://secure.gravatar.com/avatar/c70ea9cbba63cde354a9f4f3edd84ac5a3bc9dfad8c0e3cd235c6332c1ed3184?s=96&d=mm&r=g\",\"contentUrl\":\"https://secure.gravatar.com/avatar/c70ea9cbba63cde354a9f4f3edd84ac5a3bc9dfad8c0e3cd235c6332c1ed3184?s=96&d=mm&r=g\",\"caption\":\"secultthaisbezerra\"},\"url\":\"https://www.secult.ce.gov.br/author/secultthaisbezerra/\"}]}\u003c/script\u003e\n\u003c!-- / Yoast SEO plugin. --\u003e",
===========================================================================================
"yoast_head": "\u003c!-- This site is optimized with the Yoast SEO plugin v26.7 - https://yoast.com/wordpress/plugins/seo/ --\u003e\n\u003ctitle\u003eArquivos Rece - Secretaria da Cultura\u003c/title\u003e\n\u003cmeta name=\"robots\" content=\"index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1\" /\u003e\n\u003clink rel=\"canonical\" href=\"https://www.secult.ce.gov.br/category/rece/\" /\u003e\n\u003cmeta property=\"og:locale\" content=\"pt_BR\" /\u003e\n\u003cmeta property=\"og:type\" content=\"article\" /\u003e\n\u003cmeta property=\"og:title\" content=\"Arquivos Rece - Secretaria da Cultura\" /\u003e\n\u003cmeta property=\"og:url\" content=\"https://www.secult.ce.gov.br/category/rece/\" /\u003e\n\u003cmeta property=\"og:site_name\" content=\"Secretaria da Cultura\" /\u003e\n\u003cmeta name=\"twitter:card\" content=\"summary_large_image\" /\u003e\n\u003cscript type=\"application/ld+json\" class=\"yoast-schema-graph\"\u003e{\"@context\":\"https://schema.org\",\"@graph\":[{\"@type\":\"CollectionPage\",\"@id\":\"https://www.secult.ce.gov.br/category/rece/\",\"url\":\"https://www.secult.ce.gov.br/category/rece/\",\"name\":\"Arquivos Rece - Secretaria da Cultura\",\"isPartOf\":{\"@id\":\"https://www.secult.ce.gov.br/#website\"},\"breadcrumb\":{\"@id\":\"https://www.secult.ce.gov.br/category/rece/#breadcrumb\"},\"inLanguage\":\"pt-BR\"},{\"@type\":\"BreadcrumbList\",\"@id\":\"https://www.secult.ce.gov.br/category/rece/#breadcrumb\",\"itemListElement\":[{\"@type\":\"ListItem\",\"position\":1,\"name\":\"Início\",\"item\":\"https://www.secult.ce.gov.br/\"},{\"@type\":\"ListItem\",\"position\":2,\"name\":\"Rece\"}]},{\"@type\":\"WebSite\",\"@id\":\"https://www.secult.ce.gov.br/#website\",\"url\":\"https://www.secult.ce.gov.br/\",\"name\":\"Secretaria da Cultura\",\"description\":\"Secretaria da Cultura\",\"publisher\":{\"@id\":\"https://www.secult.ce.gov.br/#organization\"},\"potentialAction\":[{\"@type\":\"SearchAction\",\"target\":{\"@type\":\"EntryPoint\",\"urlTemplate\":\"https://www.secult.ce.gov.br/?s={search_term_string}\"},\"query-input\":{\"@type\":\"PropertyValueSpecification\",\"valueRequired\":true,\"valueName\":\"search_term_string\"}}],\"inLanguage\":\"pt-BR\"},{\"@type\":\"Organization\",\"@id\":\"https://www.secult.ce.gov.br/#organization\",\"name\":\"Secretaria da Cultura\",\"url\":\"https://www.secult.ce.gov.br/\",\"logo\":{\"@type\":\"ImageObject\",\"inLanguage\":\"pt-BR\",\"@id\":\"https://www.secult.ce.gov.br/#/schema/logo/image/\",\"url\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2018/05/secult-clara-3.png\",\"contentUrl\":\"https://www.secult.ce.gov.br/wp-content/uploads/sites/43/2018/05/secult-clara-3.png\",\"width\":559,\"height\":106,\"caption\":\"Secretaria da Cultura\"},\"image\":{\"@id\":\"https://www.secult.ce.gov.br/#/schema/logo/image/\"}}]}\u003c/script\u003e\n\u003c!-- / Yoast SEO plugin. --\u003e",


""")
