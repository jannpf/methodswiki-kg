import requests
import json
import urllib.parse


def get_all_articles(apiurl) -> list:
    """
    Retrieve a list of all available articles.

    Returns:
        A list with each item being a dict with keys: pageid, title, ns
    """
    request = f"{apiurl}?action=query&format=json&list=allpages&aplimit=max"
    response = requests.get(request)
    return json.loads(response.text)["query"]["allpages"]


def get_page_data(apiurl, pageid) -> dict:
    """
    Retrieve details for one specific page.

    Returns:
        Dict with keys (if each property exists):
            pageid
            ns
            title
            categories
            links
            linkshere
            contentmodel
            pagelanguage
            pagelanguagehtmlcode
            pagelanguagedir
            touched
            lastrevid
            length
            revisions (includes page content)
    """
    # properties to retrieve
    props = [
        "categories",
        "links",
        "linkshere",
        "info",
        "revisions",
        "imageinfo",
    ]

    # properties specifically for the revisions
    rvprops = [
        "content",
        "tags",
        "timestamp",
    ]

    # extra attributes like limits, specific revisions, etc
    extra_attr = [
        # only look at the main revision for now
        "rvslots=main",
        # link limit, default 10
        "pllimit=500",
        # backlink limit, default 10
        "lhlimit=500",
        # category limit, default 10
        "cllimit=500",
    ]
    extra_args = '&'.join(extra_attr)

    request = f"{apiurl}?action=query&format=json&prop={'|'.join(props)}&rvprop={'|'.join(rvprops)}&{extra_args}&pageids={pageid}"

    response = requests.get(request)
    page = json.loads(response.text)

    return page["query"]["pages"][f"{pageid}"]


def get_all_categories(apiurl) -> list:
    """
    Retrieve a list of all available categories.

    Returns:
        A list with each item being a dict with keys: pageid, title, ns
    """
    request = f"{apiurl}?action=query&format=json&list=allcategories&aclimit=max"
    response = requests.get(request)
    items = json.loads(response.text)["query"]["allcategories"]
    return [v['*'] for v in items]


def get_category_info(apiurl, title):
    """
    Retrieve more info for the given category.

    Returns:
        A dict with keys (if each property existing):
            pageid
            ns
            title
            categoryinfo (itself with: size, pages, files, subcats)
    """
    title_enc = urllib.parse.quote_plus(title)
    request = f"{apiurl}?action=query&format=json&titles=Category:{title_enc}&prop=categoryinfo"

    response = requests.get(request)
    catinfo = json.loads(response.text)["query"]["pages"]
    pageid = next(iter(catinfo))

    return catinfo[pageid]


def load_from_file(file) -> list:
    return json.load(open(file, 'r'))


def save_to_file(page, file) -> dict:
    return json.dump(page, open(file, 'w'))
