---
name: docker-start-redis
description: Check whether Docker is running and start a local Redis service with Docker Compose. Use when the user asks to start, launch, or prepare Redis in the current project, especially when docker-compose.redis.yml or ./data/redis may not exist.
---

# Start Redis with Docker

Run this workflow from the current project directory.

## Workflow

1. Check the Docker daemon with `docker info`. If it fails because Docker is not running, stop and tell the user to start Docker Desktop/the Docker daemon. Do not start the daemon yourself.

2. Ensure the data directory exists:

   ```bash
   mkdir -p ./data/redis
   ```

3. If `./docker-compose.redis.yml` exists, use it unchanged and run `docker compose -f ./docker-compose.redis.yml up -d`.

   If it does not exist, create it with this content and run `docker compose -f ./docker-compose.redis.yml up -d`:

   ```yaml
   version: "3.8"

   services:
     redis:
       image: redis:7-alpine
       container_name: redis
       restart: always
       ports:
         - "6379:6379"
       volumes:
         - ./data/redis:/data
       command: redis-server --appendonly yes --requirepass "ChangeMe123456"
   ```

4. Verify with `docker compose -f ./docker-compose.redis.yml ps` and report the service status. The default local endpoint is `localhost:6379`, and the configured password is `ChangeMe123456`. Advise changing the password for non-local use.

## Safety and failure handling

- Never overwrite an existing Compose file.
- Report errors from Compose instead of rewriting a user's existing configuration.
- Common failures include port `6379` being occupied, an existing container named `redis`, or Docker not running.
