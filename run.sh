#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

# Colors for readability
G="\033[0;32m"
Y="\033[0;33m"
R="\033[0;31m"
N="\033[0m"

say() { printf "${G}==>${N} %s\n" "$1"; }
warn() { printf "${Y}!!>${N} %s\n" "$1"; }
die() { printf "${R}xx>${N} %s\n" "$1" >&2; exit 1; }

# Make sure docker exists
command -v docker >/dev/null 2>&1 || die "Docker is not installed."
docker info >/dev/null 2>&1 || die "Docker daemon not running. Start it with: sudo systemctl start docker"

# Make sure compose file is present
[ -f compose.yml ] || die "compose.yml not found in $(pwd)"

# Build image on run
if ! docker image inspect vel:latest >/dev/null 2>&1; then
    say "First run: building image..."
    docker compose build
else
    # Rebuild silently if Dockerfile or requirements changed
    if [ Dockerfile -nt .vel-built ] 2>/dev/null || [ requirements.txt -nt .vel-built ] 2>/dev/null; then
        say "Dependencies changed, rebuilding..."
        docker compose build
    fi
fi
touch .vel-built

# Clean up any leftover containers
docker compose down --remove-orphans >/dev/null 2>&1 || true

# Hand over the terminal to the CLI
say "Starting VEL..."
exec docker compose run --rm vel
