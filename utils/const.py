JORNAIS_MAP = {
    "opovo": {
        "url": "https://www.opovo.com.br/index.php",
        "params": {
            "id": "/reboot/src/endpoints/VerMais.php",
            "dinamico": 1,
            "site_arvor": "Vida&Arte",
            "limit": 30,
        },
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
    "dn": {
        "url": "https://diariodonordeste.verdesmares.com.br/ceara",
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
    "oestadoce": {
        "url": "https://oestadoce.com.br/wp-json/wp/v2/posts",
        "params": {"categories": "8", "page": "1", "per_page": "30"},
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
    "verdemares": {
        "url": "https://g1.globo.com/rss/g1/ce/ceara",
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
    "cearaagora": {
        "url": "https://cearaagora.com.br/wp-json/wp/v2/posts",
        "params": {"page": "1", "per_page": "30"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    },
    "tce": {
        "url": "https://www.tce.ce.gov.br/comunicacao/noticias",
        "params": {"format": "feed", "type": "atom", "start": "0"},
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
    "terra_da_luz": {
        "url": "https://portalterradaluz.com.br/wp-json/wp/v2/posts",
        "params": {"page": "1", "per_page": "30"},
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
    "jangadeiro": {
        "url": "https://www.jangadeiro.com.br/wp-json/wp/v2/posts",
        "params": {
            "_embed": "true",
            "per_page": "30",
            "page": "1",
        },
        "headers": {"User-Agent": "Mozilla/5.0"},
    },
}
