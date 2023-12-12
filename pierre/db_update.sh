docker-compose cp pierre/create_token.sh db:./
docker-compose exec db /bin/bash create_token.sh