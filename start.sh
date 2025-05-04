#!/bin/bash

# Start cron jobs
cron &

# Start FastAPI app
uvicorn app:app --host 0.0.0.0 --port 8000 &

# Start Streamlit app
streamlit run /ninja/dash/home.py --server.port=8501 --server.address=0.0.0.0
