# Dockerfile para proyecto Django en Coolify
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias primero para aprovechar cache de Docker
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia el resto del proyecto
COPY . .

# Opcional: recopila archivos estáticos para producción
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
