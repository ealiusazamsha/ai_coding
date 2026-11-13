FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Fail during image build if the API is invalid or WebSocket support is missing.
RUN python -m compileall -q app \
    && python -c "import websockets; from app.main import app; assert any(route.path == '/ws/v1/demo' for route in app.routes), 'WebSocket endpoint missing'"
RUN useradd --create-home --uid 10001 aacp
USER aacp
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
