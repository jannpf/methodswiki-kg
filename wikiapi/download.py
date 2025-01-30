from api import *

wikiurl = "https://sustainabilitymethods.org"
apiurl = f"{wikiurl}/api.php"


# all_articles = get_all_articles(apiurl)
# save_to_file(all_articles, "all_articles.json")
all_articles = load_from_file("all_articles.json")

for a in all_articles:
    print(a)
    pageid = a["pageid"]
    article_content = get_page_data(apiurl, pageid)
    save_to_file(article_content, f"articles/{pageid}.json")


# all_categories = get_all_categories(apiurl)
# save_to_file(all_categories, "all_categories.json")
all_categories = load_from_file("all_categories.json")

for c in all_categories:
    print(c)
    catinfo = get_category_info(apiurl, c)
    pageid = catinfo["pageid"]
    cat_data = get_page_data(apiurl, pageid)
    cat_data.update(catinfo)

    save_to_file(cat_data, f"categories/{pageid}.json")
