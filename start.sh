#!/bin/bash
source /home/talles/analisevoz/phonia_v0/phonia/venv/bin/activate
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
