#!/bin/sh

# Start Nginx
nginx -g 'daemon off;' &

# Watch for changes in the /usr/share/nginx/html directory
while inotifywait -e modify,create,delete -r /usr/share/nginx/html; do
    nginx -s reload
done
