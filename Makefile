.PHONY: all build up down stop clean logs wipe restart frontend-dev frontend-build frontend-install

# Default target
all: build up

# Build the application image
build:
	podman build --network=host -t localhost/jobflow_app:latest .

# Start containers in the background using podman-compose
# SAFE: This does NOT delete your database data. It reuses existing data.
up:
	@echo "Starting containers... (Your database data is SAFE)"
	podman-compose up -d

# Stop and remove containers and networks
# SAFE: This does NOT delete your database data.
down:
	@echo "Stopping containers... (Your database data is SAFE)"
	podman-compose down

# Stop the containers without removing them
# SAFE: This does NOT delete your database data.
stop:
	@echo "Stopping containers... (Your database data is SAFE)"
	podman-compose stop

# View the application logs
logs:
	podman-compose logs -f

# Clean up stopped containers, unused networks, and dangling images
# SAFE: This does NOT delete your database data.
clean:
	@echo "Cleaning up stopped containers and dangling images... (Your database data is SAFE)"
	podman container prune -f
	podman image prune -f

# Completely restart everything and build
# SAFE: This does NOT delete your database data.
restart: down build up

# ── Frontend (React 19 + TypeScript + Vite) ──────────────────────────────────
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# ⚠️ DANGER: Wipes EVERYTHING including the database volume!
# WARNING: THIS WILL MAKE YOUR DATA ON DATABASE DISAPPEAR!
wipe:
	@echo "⚠️ WARNING: THIS WILL MAKE YOUR DATA ON DATABASE DISAPPEAR! ⚠️"
	@echo "Removing containers and deleting the database volume..."
	podman-compose down -v
