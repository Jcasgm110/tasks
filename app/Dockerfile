# fase 1: instalar as dependências
FROM python:3.14-slim AS builder
WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# fase 2: imagem final
FROM python:3.14-slim
RUN useradd --create-home --shell /usr/sbin/nologin appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /home/appuser/app
COPY --chown=appuser:appuser app.py .
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]