from dataclasses import dataclass

import yaml


@dataclass
class Quote(yaml.YAMLObject):
    yaml_tag = "Quote"

    quote: str
    author: str
    title: str

    def __init__(self, quote: str, author: str = "", title: str = ""):
        self.quote = quote.strip()
        self.author = author.strip()
        self.title = title.strip()

    @staticmethod
    def from_dict(d: dict) -> "Quote":
        return Quote(
            quote=d.get("quote", "").strip(),
            author=d.get("author", "").strip(),
            title=d.get("title", "").strip(),
        )

    def to_dict(self) -> dict:
        return dict(quote=self.quote, author=self.author, title=self.title)

    def to_message(self) -> str:
        return f"""{self.quote}
{self.print_meta()}"""

    def print_meta(self) -> str:
        return "- " + ", ".join([self.author, self.title])
