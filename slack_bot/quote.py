from dataclasses import dataclass
from typing import List

import yaml


@dataclass
class Quote(yaml.YAMLObject):
    yaml_tag = "Quote"

    quote: str
    author: str
    title: str
    skip: bool

    def __init__(
        self, quote: str, author: str = "", title: str = "", skip: bool = False
    ):
        self.quote = quote.strip()
        self.author = author.strip()
        self.title = title.strip()
        self.skip = skip

    def __hash__(self) -> int:
        return hash((self.quote, self.author, self.title, self.skip))

    @staticmethod
    def from_dict(d: dict) -> "Quote":
        return Quote(
            quote=d.get("quote", "").strip(),
            author=d.get("author", "").strip(),
            title=d.get("title", "").strip(),
            skip=d.get("skip", False),
        )

    def to_dict(self) -> dict:
        return dict(
            quote=self.quote, author=self.author, title=self.title, skip=self.skip
        )

    def to_message(self) -> str:
        return f"""{self.quote}
{self.print_meta()}"""

    def print_meta(self) -> str:
        if self.title == "":
            return f"- {self.author}"

        if self.author == "":
            return f"- {self.title}"

        return "- " + ", ".join([self.author, self.title])


def load_quotes() -> List[Quote]:
    data = []
    with open("slack_bot/saying.yaml", "r") as f:
        for q_dict in yaml.safe_load(f):
            quote = Quote.from_dict(q_dict)
            if not quote.skip:
                data.append(quote)
    return data
