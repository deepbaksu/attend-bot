#!/usr/bin/env bash

docker run -it -p 5432:5432 --rm -e POSTGRES_PASSWORD=password postgres
