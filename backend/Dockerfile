FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
# We assume the docker-compose context will be the root directory
# so we can copy ml models if needed.
COPY . /app/backend
COPY ../ml /app/ml

# The main.py will be executed from within /app/backend
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
