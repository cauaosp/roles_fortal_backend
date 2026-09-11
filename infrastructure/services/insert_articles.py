from infrastructure.database import engine
from infrastructure.model.article import Article
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from utils.helpers import normalize_category, parse_date


def save_articles_to_db(articles: dict) -> int:
    """Insere ou atualiza artigos pelo link. Ignora duplicatas."""
    Session = sessionmaker(bind=engine)
    session = Session()
    saved = 0

    try:
        for art in articles.values():
            pub_date = parse_date(art.get("publication_date"))
            scrap_date = parse_date(art.get("scraped_at"))
            category = normalize_category(art.get("category"))

            stmt = (
                insert(Article)
                .values(
                    title=art["title"],
                    subtitle=art.get("subtitle"),
                    author=art.get("author"),
                    category=category,
                    link=art["link"],
                    journal=art["journal"],
                    publication_date=pub_date,
                    scraped_at=scrap_date,
                )
                .on_conflict_do_update(
                    index_elements=["link"],
                    set_={
                        "title": art["title"],
                        "subtitle": art.get("subtitle"),
                        "author": art.get("author"),
                        "category": category,
                        "journal": art["journal"],
                        "publication_date": pub_date,
                        "scraped_at": scrap_date,
                    },
                )
            )

            session.execute(stmt)
            saved += 1

        session.commit()
        print(f"✅ {saved} artigos processados (insert/update)")
        return saved

    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        session.close()
