FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .
COPY src/ src/
EXPOSE 8088
CMD ["uvicorn", "enterprise_ai_platform.main:app", "--host", "0.0.0.0", "--port", "8088"]
