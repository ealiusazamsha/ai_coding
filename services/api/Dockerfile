FROM python:3.12-slim AS api-base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Fail during image build if source is malformed, an import fails, or WS support is absent.
RUN python -m compileall -q app \
    && python -c "import websockets; from app.main import app; assert any(route.path == '/ws/v1/demo' for route in app.routes), 'WebSocket endpoint missing'"

# Build explicitly with: docker build --target tests -t aacp-api-tests ./services/api
FROM api-base AS tests
ENV AACP_ENV=test AACP_DEMO_MODE=true
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
RUN python -m compileall -q tests && pytest -q

FROM api-base AS runtime
RUN useradd --create-home --uid 10001 aacp
USER aacp
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
