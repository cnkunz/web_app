# web_app
This is a demo of a docker stack including a Python API that interfaces with a maridb database.

Both the web application and the maridb are in seperate containers connected via docker bridge.

# Usage
- Pull repo down
- Build docker images
    - docker build web_app/app/ -t web_app
    - docker build web_app/mariadb/ -t productdb
- Run docker compose
    - docker-compose up -d
- Wait for database to start fully
- Run tests from postman or other API testing framework
