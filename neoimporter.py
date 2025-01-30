from neo4j import GraphDatabase
from page import Page
from category import Category


class NeoImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def import_article(self, article):
        with self.driver.session() as session:
            session.execute_write(self.create_article_node, article)

    def import_category(self, article):
        with self.driver.session() as session:
            session.execute_write(self.create_article_node, article)

    @staticmethod
    def create_article_node(tx, page: Page):
        tx.run("""
                MERGE (a:Article {title: $title})
                SET a.pageid = $pageid,
                    a.url = $url,
                    a.pageid = $pageid
                    a.ns = $ns
                    a.contentmodel = $contentmodel
                    a.pagelanguage = $pagelanguage
                    a.touched = $touched
                    a.length = $length
                    a.text = $text
                """,
               title=page.title,
               pageid=page.pageid,
               url=page.url,
               pageid=page.pageid,
               ns=page.ns,
               contentmodel=page.contentmodel,
               pagelanguage=page.pagelanguage,
               touched=page.touched,
               length=page.length,
               text=page.get_text(),
               )

        for category in page.get("categories", []):
            tx.run("""
                MERGE (c:Category {name: $name})
                MERGE (a:Article {title: $title})
                MERGE (a)-[r:CATEGORIZED_AS]->(c)
                """,
                   name=category,
                   title=page["title"])

        for link in page.get("links", []):
            tx.run("""
                MERGE (a1:Article {title: $from_title})
                MERGE (a2:Article {title: $to_title})
                MERGE (a1)-[r:LINKS_TO]->(a2)
                """,
                   from_title=page["title"],
                   to_title=link["title"])

    @staticmethod
    def create_category_node(tx, category: Category):
        tx.run("""
                MERGE (c:Category {name: $title})
                SET c.pageid = $pageid,
                    c.url = $url,
                    c.pageid = $pageid
                    c.ns = $ns
                    c.contentmodel = $contentmodel
                    c.pagelanguage = $pagelanguage
                    c.touched = $touched
                    c.length = $length
                    c.text = $text
                    c.size = $size
                    c.pages = $pages
                    c.files = $files
                    c.subcats = $subcats
                """,
               name=category.title,
               pageid=category.pageid,
               url=category.url,
               pageid=category.pageid,
               ns=category.ns,
               contentmodel=category.contentmodel,
               pagelanguage=category.pagelanguage,
               touched=category.touched,
               length=category.length,
               text=category.get_text(),
               size=category.size,
               pages=category.pages,
               files=category.files,
               subcats=category.subcats,
               )

        for supercats in category.get("categories", []):
            tx.run("""
                MERGE (a:Category {name: $name})
                MERGE (c:Category {title: $title})
                MERGE (a)-[r:CATEGORIZED_AS]->(c)
                """,
                   name=category["title"],
                   title=supercats["title"])

        for link in category.get("links", []):
            tx.run("""
                MERGE (c:Category {title: $from_title})
                MERGE (a:Article {title: $to_title})
                MERGE (c)-[r:LINKS_TO]->(a)
                """,
                   from_title=category["title"],
                   to_title=link["title"])
