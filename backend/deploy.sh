#!/usr/bin/env bash
# Campus Smart Service - safe server deployment helper.
# Usage after cloning the GitHub repository:
#   cd campus-smart-service/backend
#   cp .env.example .env
#   # edit .env: JWT_SECRET, ADMIN_USERNAME, ADMIN_PASSWORD, API keys, domains
#   bash deploy.sh

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/campus-smart-service}"
WEB_DIR="${WEB_DIR:-/var/www/rag-user}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.server.yml}"
SEED_HBU_DEMO_DATA="${SEED_HBU_DEMO_DATA:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================"
echo " Campus Smart Service deployment"
echo " Host: $(hostname) ($(hostname -I 2>/dev/null | awk '{print $1}'))"
echo " Backend source: $SCRIPT_DIR"
echo " Project dir: $PROJECT_DIR"
echo " Web dir: $WEB_DIR"
echo "========================================"

need_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this deployment script as root or through sudo."
    exit 1
  fi
}

compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    echo "Docker Compose is not available."
    exit 1
  fi
}

install_docker_if_needed() {
  echo "[1/7] Checking Docker..."
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker not found. Installing Docker through get.docker.com..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
  fi

  if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    echo "Docker Compose plugin not found. Installing docker-compose-plugin..."
    apt-get update
    apt-get install -y docker-compose-plugin
  fi
  echo "Docker ready: $(docker --version)"
}

prepare_project_dir() {
  echo "[2/7] Preparing project directory..."
  mkdir -p "$PROJECT_DIR"
  if [ "$REPO_DIR" != "$PROJECT_DIR" ]; then
    rsync -a --delete \
      --exclude '.git/' \
      --exclude '.venv/' \
      --exclude 'node_modules/' \
      --exclude 'backend/.env' \
      --exclude 'backend/*.db' \
      --exclude 'backend/*.bak' \
      --exclude 'test-results/' \
      "$REPO_DIR/" "$PROJECT_DIR/"
  fi
}

prepare_env() {
  echo "[3/7] Checking backend .env..."
  cd "$PROJECT_DIR/backend"
  if [ ! -f .env ]; then
    cp .env.example .env
    if command -v openssl >/dev/null 2>&1; then
      JWT_SECRET_VALUE="$(openssl rand -hex 32)"
      POSTGRES_PASSWORD_VALUE="$(openssl rand -hex 18)"
      sed -i "s/^JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET_VALUE}/" .env
      sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${POSTGRES_PASSWORD_VALUE}/" .env
    fi
    echo "Created backend/.env from .env.example. Please review admin accounts, API keys, and domain settings."
  fi

  if grep -q '^JWT_SECRET=change-this' .env; then
    echo "ERROR: JWT_SECRET is still using an example value. Edit backend/.env before production deployment."
    exit 1
  fi
  if ! grep -Eq '^ADMIN_USERNAME=.+$' .env || ! grep -Eq '^ADMIN_PASSWORD=.+$' .env; then
    echo "ERROR: ADMIN_USERNAME and ADMIN_PASSWORD must be set in backend/.env."
    exit 1
  fi
}

deploy_web_static() {
  echo "[4/7] Deploying Web static files..."
  mkdir -p "$WEB_DIR"
  install -m 0644 "$PROJECT_DIR/index.html" "$WEB_DIR/index.html"
  install -m 0644 "$PROJECT_DIR/app.js" "$WEB_DIR/app.js"
  install -m 0644 "$PROJECT_DIR/styles.css" "$WEB_DIR/styles.css"
  if [ -f "$PROJECT_DIR/favicon.svg" ]; then
    install -m 0644 "$PROJECT_DIR/favicon.svg" "$WEB_DIR/favicon.svg"
  fi
}

start_backend() {
  echo "[5/7] Building and starting backend stack..."
  cd "$PROJECT_DIR/backend"
  if [ ! -f "$COMPOSE_FILE" ]; then
    echo "ERROR: compose file not found: $PROJECT_DIR/backend/$COMPOSE_FILE"
    exit 1
  fi
  compose_cmd -f "$COMPOSE_FILE" up -d --build
}

wait_for_health() {
  echo "[6/7] Waiting for backend health..."
  for _ in $(seq 1 60); do
    if curl -fsS http://127.0.0.1:8000/healthz >/dev/null 2>&1; then
      echo "Backend health check passed."
      return 0
    fi
    sleep 2
  done
  echo "ERROR: backend did not become healthy in time."
  compose_cmd -f "$COMPOSE_FILE" logs api --tail 80 || true
  exit 1
}

seed_demo_data_if_requested() {
  echo "[7/7] Optional demo data rebuild..."
  cd "$PROJECT_DIR/backend"
  if [ "$SEED_HBU_DEMO_DATA" = "1" ]; then
    compose_cmd -f "$COMPOSE_FILE" exec -T api python scripts/seed_hbu_realistic_demo_data.py
  else
    echo "Skipped demo seed data. Set SEED_HBU_DEMO_DATA=1 to rebuild HBU demo data."
  fi
}

need_root
install_docker_if_needed
prepare_project_dir
prepare_env
deploy_web_static
start_backend
wait_for_health
seed_demo_data_if_requested

echo "========================================"
echo " Deployment completed."
echo " Backend: http://127.0.0.1:8000/healthz"
echo " Web files: $WEB_DIR"
echo " Data is stored in Docker volumes and is not committed to GitHub."
echo "========================================"
