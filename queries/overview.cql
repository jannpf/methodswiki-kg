MATCH (n)
WHERE (n:Article AND NOT (n.pageid IN [148, 399]))
   OR (n:Category)
RETURN n;