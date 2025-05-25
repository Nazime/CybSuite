#!/bin/bash

poetry run uvicorn cybsuite.api.main:app --reload  --reload-dir src/cybsuite/ --port 2501 --host 0.0.0.0