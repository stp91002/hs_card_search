#!/bin/bash
docker create \
  --hostname card_mysql \
  --name card_mysql \
  -p 3306:3306 \
  -v $(pwd)/mysql_data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=1234 \
  mysql:5.7.27
