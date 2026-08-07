---
name: docker-start-minio
description: Check whether Docker is running and start a local MinIO service with Docker Compose. Use when the user asks to start, launch, or prepare MinIO in the current project, especially when docker-compose-minio.yml or ./data/minio may not exist.
---

# Start MinIO with Docker

Run this workflow from the current project directory.

## Workflow

1. Check that the Docker daemon is available:

   ```bash
   docker info
   ```

   If this check fails because Docker is not running, stop immediately and tell the user to start Docker Desktop/the Docker daemon, then retry. Do not attempt to start the daemon yourself.

2. Check for both `./docker-compose-minio.yml` and `./data/minio`.

   - If `./data/minio` is missing, create its data and config directories:

     ```bash
     mkdir -p ./data/minio/{data,config}
     ```

   - If `./docker-compose-minio.yml` is missing, create it with this content. Do not overwrite an existing Compose file.

     ```yaml
     version: "3.8"

     services:
       minio:
         image: pgsty/minio:RELEASE.2026-03-25T00-00-00Z
         container_name: minio

         restart: always

         ports:
           - "9000:9000"
           - "9001:9001"

         environment:
           MINIO_ROOT_USER: admin
           MINIO_ROOT_PASSWORD: "ChangeMe123456"
         volumes:
           - ./data/minio/data:/data
           - ./data/minio/config:/root/.minio

         command: server /data --console-address ":9001"
     ```

3. Start the service, whether the files already existed or were just created:

   ```bash
   docker compose -f docker-compose-minio.yml up -d
   ```

4. Verify the result with:

   ```bash
   docker compose -f docker-compose-minio.yml ps
   ```

   Report the service status and, if it is running, the MinIO API (`http://localhost:9000`) and console (`http://localhost:9001`) addresses. The configured local credentials are `admin` / `ChangeMe123456`; mention that the password should be changed for non-local use.

## Safety and failure handling

- Never overwrite an existing `docker-compose-minio.yml` during setup.
- If an existing Compose file uses different service names, ports, or volume paths, preserve it and run `docker compose -f docker-compose-minio.yml up -d` as requested; report any startup error instead of rewriting the file.
- If `docker compose -f docker-compose-minio.yml up -d` fails, inspect `docker compose -f docker-compose-minio.yml ps` and provide the relevant error. Common causes include ports `9000` or `9001` already being occupied, an existing container named `minio`, or Docker not having started.
