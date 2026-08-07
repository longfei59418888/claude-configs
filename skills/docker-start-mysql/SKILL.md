---
name: docker-start-mysql
description: Check whether Docker is running and start a local MySQL service with Docker Compose. Use when the user asks to start, launch, or prepare MySQL in the current project, especially when docker-compose.mysql.yml or ./data/mysql may not exist.
---

# Start MySQL with Docker

Run this workflow from the current project directory.

## Workflow

1. Check the Docker daemon with `docker info`. If it fails because Docker is not running, stop and tell the user to start Docker Desktop/the Docker daemon. Do not start the daemon yourself.

2. Ensure the data directory exists:

   ```bash
   mkdir -p ./data/mysql
   ```

3. If `./docker-compose.mysql.yml` exists, use it unchanged and run `docker compose -f ./docker-compose.mysql.yml up -d`.

   If it does not exist, create it with this content and run `docker compose -f ./docker-compose.mysql.yml up -d`:

   ```yaml
   version: "3.8"

   services:
     mysql:
       image: mysql:8.4
       container_name: mysql
       restart: always
       ports:
         - "3306:3306"
       environment:
         MYSQL_ROOT_PASSWORD: "ChangeMe123456"
         MYSQL_DATABASE: app
       volumes:
         - ./data/mysql:/var/lib/mysql
   ```

4. Verify with `docker compose -f ./docker-compose.mysql.yml ps` and report the service status. The default local connection is `localhost:3306`, root password is `ChangeMe123456`, and the default database is `app`. Advise changing the password for non-local use.

## Safety and failure handling

- Never overwrite an existing Compose file.
- Report errors from Compose instead of rewriting a user's existing configuration.
- Common failures include port `3306` being occupied, an existing container named `mysql`, or Docker not running.
