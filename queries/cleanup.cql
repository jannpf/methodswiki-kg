// every category is also a page,
// but we treat them as separate entities
MATCH (n:Article)
WHERE n.title STARTS WITH "Category:"  
DETACH DELETE n;

// delete table of contributors, as its linked to most pages
// MATCH (n:Article {pageid: 148}) DETACH DELETE n;

// delete glossary, as its linked to most pages
// MATCH (n:Article {pageid: 399}) DETACH DELETE n;
