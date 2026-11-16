FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the MCP server files
COPY ./src/ /app/

CMD ["python", "-m", "traefik_mcp"]

