# ----------------------------------------------------------------------------
# Étape 1 : build — on compile les dépendances en "wheels"
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ----------------------------------------------------------------------------
# Étape 2 : runtime — image finale légère, sans outils de build
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Bonnes pratiques Python en conteneur
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# On installe les dépendances pré-compilées (rapide, pas de toolchain dans l'image)
COPY requirements.txt .
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

COPY app ./app

# Utilisateur non-root pour la sécurité
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
