---
name: docker-start-postgresql
description: Check whether Docker is running and start a local PostgreSQL service with Docker Compose. Use when the user asks to start, launch, or prepare PostgreSQL in the current project, especially when docker-compose.postgresql.yml or ./data/postgresql may not exist.
---

# Start PostgreSQL with Docker

Run this workflow from the current project directory.

## Workflow

1. Check the Docker daemon with `docker info`. If it fails because Docker is not running, stop and tell the user to start Docker Desktop/the Docker daemon. Do not start the daemon yourself.

2. Ensure the data directory exists:

   ```bash
   mkdir -p ./data/postgresql
   ```

3. If `./docker-compose.postgresql.yml` exists, use it unchanged and run `docker compose -f ./docker-compose.postgresql.yml up -d`.

   If it does not exist, create it with this content and run `docker compose -f ./docker-compose.postgresql.yml up -d`:

   ```yaml
   version: "3.8"

   services:
     postgres:
       image: postgres:16
       container_name: postgresql
       restart: always
       ports:
         - "5432:5432"
       environment:
         POSTGRES_USER: admin
         POSTGRES_PASSWORD: "ChangeMe123456"
         POSTGRES_DB: app
       volumes:
         - ./data/postgresql:/var/lib/postgresql/data
   ```

4. Verify with `docker compose -f ./docker-compose.postgresql.yml ps` and report the service status. The default local connection is `localhost:5432`, with user `admin`, database `app`, and password `ChangeMe123456`. Advise changing the password for non-local use.

## Safety and failure handling

- Never overwrite an existing Compose file.
- Report errors from Compose instead of rewriting a user's existing configuration.
- Common failures include port `5432` being occupied, an existing container named `postgresql`, or Docker not running.
