from dataclasses import dataclass, field

from page import Page


@dataclass(unsafe_hash=True)
class Category(Page):
    categoryinfo: dict = field(default_factory=lambda: {})

    @property
    def size(self) -> int:
        return self.categoryinfo["size"]

    @property
    def pages(self) -> int:
        return self.categoryinfo["pages"]

    @property
    def files(self) -> int:
        return self.categoryinfo["files"]

    @property
    def subcats(self) -> int:
        return self.categoryinfo["subcats"]
