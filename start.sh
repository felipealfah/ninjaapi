#!/bin/bash

# Start cron in the background
cron &

# Start FastAPI app using Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000
