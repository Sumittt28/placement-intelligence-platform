#!/bin/bash
cd /opt/render/project/src/backend || cd backend || true
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
