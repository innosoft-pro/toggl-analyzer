#!/usr/bin/env bash
docker rm $(docker stop toggl_nginx)
docker build -t toggl .
docker run --name toggl_nginx -d -p 8888:80 toggl
