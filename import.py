import glob

from wikiapi import api
from neoimporter import NeoImporter
from entities.category import Category
from entities.page import Page

importer = NeoImporter("neo4j://localhost:7687", "neo4j", "12341234")

category_files = glob.glob("wikiapi/categories/*.json")
for c in category_files:
    category_dict = api.load_from_file(c)
    category: Category = Category.from_dict(category_dict)
    importer.import_category(category)

article_files = glob.glob("wikiapi/articles/*.json")
for a in article_files:
    article_dict = api.load_from_file(a)
    page: Page = Page.from_dict(article_dict)
    importer.import_article(page)


# importer.clear_entity("Article")
# importer.clear_entity("Category")
