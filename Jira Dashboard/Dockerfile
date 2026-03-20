# Build context: repo root (required — server.py imports secrets_loader.py from parent)
# docker build -f "Jira Dashboard/Dockerfile" -t jira-dashboard .
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY "Jira Dashboard/requirements.txt" requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules from repo root
COPY secrets_loader.py ./
COPY llm_gateway.py ./

# Copy app source
COPY "Jira Dashboard/" ./

ENV PORT=8080
EXPOSE 8080

CMD ["python3", "server.py"]
