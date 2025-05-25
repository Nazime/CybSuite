#!/bin/bash
set -e
pipx install -e . --force

docker-compose up --build

poetry run uvicorn cybsuite.api.main:app --reload  --reload-dir src/cybsuite/ --port 2501