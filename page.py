import json
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus


@dataclass(unsafe_hash=True)
class Page:
    pageid: int
    ns: int
    title: str
    lastrevid: int
    length: int
    revisions: list
    categories: list = field(default_factory=lambda: [])
    links: list = field(default_factory=lambda: [])
    linkshere: list = field(default_factory=lambda: [])
    contentmodel: str = field(default="")
    pagelanguage: str = field(default="")
    pagelanguagehtmlcode: str = field(default="")
    pagelanguagedir: str = field(default="")
    new: str = field(default="")
    touched: str = field(default="")
    redirect: str = field(default="")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

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

    @property
    def url(self) -> str:
        return f"https://sustainabilitymethods.org/index.php/{quote_plus(self.title)}"

    def __repr__(self) -> str:
        return f"Page {{title: '{self.title}', pageid: {self.pageid}, ns: {self.ns}}}"
