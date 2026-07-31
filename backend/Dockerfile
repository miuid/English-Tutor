FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "."

# Copy application code
COPY app/ ./app/
COPY seed.py ./

# Skills are mounted from the host at runtime via docker-compose volume
# (see docker-compose.yml)

# Data volume for persistent SQLite
VOLUME ["/data"]
ENV DATABASE_URL=sqlite:////data/english_tutor.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
