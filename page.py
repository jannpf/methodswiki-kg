import json
from dataclasses import dataclass, field, make_dataclass, asdict


@dataclass(unsafe_hash=True)
class Page:
    pageid: int
    ns: int
    title: str
    categories: list
    links: list
    linkshere: list
    contentmodel: str
    pagelanguage: str
    pagelanguagehtmlcode: str
    pagelanguagedir: str
    touched: str
    lastrevid: int
    length: int
    revisions: list

    @staticmethod
    def from_dict(data: dict):
        types = ((k, type(v)) for k, v in data.items())
        return make_dataclass("Page", types)(**data)

    @staticmethod
    def from_file(filename: str):
        content = json.load(open(filename, 'r'))
        return Page.from_dict(content)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_file(self, filename: str) -> None:
        json.dump(self.to_dict(), open(filename, 'w'))

    def get_text(self) -> str:
        return self.revisions[0]["slots"]["main"]["*"]
