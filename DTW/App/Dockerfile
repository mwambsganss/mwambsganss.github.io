# Build context: repo root (required — server.py imports secrets_loader.py from parent)
# docker build -f "DTW/App/Dockerfile" -t dtw-app .
FROM python:3.12-slim

WORKDIR /app

# System deps for python-docx / python-pptx (lxml needs libxml2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY "DTW/App/requirements.txt" requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules from repo root
COPY secrets_loader.py ./

# Copy app source
COPY "DTW/App/" ./

ENV PORT=5001
EXPOSE 5001

CMD ["python3", "server.py"]
