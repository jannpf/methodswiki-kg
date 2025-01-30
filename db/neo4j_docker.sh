#!/bin/bash

docker run \
    --detach \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=./data:/data \
    --name=neo4j_wiki \
    neo4j:5.26.1

    # --env NEO4J_AUTH=neo4j/neo4j \
