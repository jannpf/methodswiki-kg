from dataclasses import dataclass

from .page import Page


@dataclass(unsafe_hash=True)
class Category(Page):
    size: int
    pages: int
    files: int
    subcats: int
