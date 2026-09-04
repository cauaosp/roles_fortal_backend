import dataclasses
from datetime import datetime, timedelta, timezone


@dataclasses.dataclass
class Article:
    title: str
    subtitle: str
    category: list[str] | None
    author: str
    publicationDate: str
    link: str
    journal: str
    createdAt: datetime


    def __post_init__(self):
        if self.category is None:
            self.category = []

    def __repr__(self):
        return f"Artigo: \ntitle={self.title},\nsubtitle={self.subtitle},\ncategory={self.category},\nauthor={self.author},\npublication_date={self.publicationDate},\nlink={self.link},\njournal={self.journal},\ncreatedAt={self.createdAt}"



def teste():
    artigo1 =  Article(
       title="Fortaleza vence clássico",
       subtitle="Time alvinegro domina rival",
       category=["esporte", "futebol", "fortaleza"],
       author="João Silva",
       publicationDate=str(datetime.now(timezone(timedelta(hours=-3)))),
       link="https://exemplo.com/artigo",
       journal="Diário do Nordeste",
       createdAt=datetime.now(timezone(timedelta(hours=-3)))
   )
    print("teste")
    print(artigo1)

teste()
