import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Article:
    title: str
    subtitle: str | None
    category: list[str] | None
    author: str | None
    publicationDate: str | None
    link: str | None
    journal: str
    createdAt: datetime


    def __post_init__(self):
        """Valida e normaliza os campos"""
        # Converte None para valores padrão
        self.title = self.title or ""
        self.subtitle = self.subtitle or ""
        self.category = self.category or []
        self.author = self.author or ""
        self.publicationDate = self.publicationDate or ""
        self.link = self.link or ""

        if not self.title:
            raise ValueError("Title é obrigatório!")

        if not self.journal:
            raise ValueError("Journal é obrigatório!")

        if not isinstance(self.createdAt, datetime):
            raise TypeError("createdAt deve ser datetime!")

    def to_dict(self) -> dict:
        """Converte para dicionário serializável"""
        return {
            "titulo": self.title,
            "subtitulo": self.subtitle,
            "categoria": self.category,
            "autor": self.author,
            "dataPublicacao": self.publicationDate,
            "link": self.link,
            "jornal": self.journal,
            "createdAt": self.createdAt.isoformat() if isinstance(self.createdAt, datetime) else self.createdAt
        }

    def __repr__(self):
        return f"Artigo: \ntitle={self.title},\nsubtitle={self.subtitle},\ncategory={self.category},\nauthor={self.author},\npublication_date={self.publicationDate},\nlink={self.link},\njournal={self.journal},\ncreatedAt={self.createdAt}"
