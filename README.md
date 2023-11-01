server
======

API Server for Internet Archive which lives at https://api.archivelab.org. See documentation at: https://archive.readme.io


## Images

Reverse image search:

https://api.archivelab.org/v2/images

Example:

curl -F "img=@stairway.png" http://api.archivelab.org:1234/v2/images

## Restarting Production Server

```
ssh api.archivelab.org
tmux
cd /var/www/api.archivelab.org/server
uwsgi --ini uwsgi.ini
```
