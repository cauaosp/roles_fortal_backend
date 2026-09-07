import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Article:
    title: str
    subtitle: str | None
    category: list[str] | None
    author: str | None
    publication_date: datetime | None
    link: str | None
    journal: str
    scraped_at: datetime


    def __post_init__(self):
        """Valida e normaliza os campos"""
        self.title = self.title or ""
        self.subtitle = self.subtitle or ""
        self.category = self.category or []
        self.author = self.author or ""
        self.publication_date = self.publication_date or None
        self.link = self.link or ""

        if not self.title:
            raise ValueError("Title é obrigatório!")

        if not self.journal:
            raise ValueError("Journal é obrigatório!")

        if not isinstance(self.scraped_at, datetime):
            raise TypeError("scraped_at deve ser datetime!")

    def to_dict(self) -> dict:
        """Converte para dicionário serializável"""
        return {
            "titulo": self.title,
            "subtitulo": self.subtitle,
            "categoria": self.category,
            "autor": self.author,
            "dataPublicacao": self.publication_date.isoformat() if isinstance(self.publication_date, datetime) else self.publication_date,
            "link": self.link,
            "jornal": self.journal,
            "scraped_at": self.scraped_at.isoformat() if isinstance(self.scraped_at, datetime) else self.scraped_at
        }

    def __repr__(self):
        return f"Artigo: \ntitle={self.title},\nsubtitle={self.subtitle},\ncategory={self.category},\nauthor={self.author},\npublication_date={self.publication_date},\nlink={self.link},\njournal={self.journal},\nscraped_at={self.scraped_at}"
