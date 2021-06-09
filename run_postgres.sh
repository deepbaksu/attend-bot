#!/usr/bin/env bash

docker run -it -p 5432:5432 --name postgres --rm -e POSTGRES_PASSWORD=password postgres