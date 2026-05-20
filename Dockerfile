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

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Run migrations
RUN python manage.py migrate --noinput || true

# Create admin user dario
RUN python manage.py shell -c "from django.contrib.auth.models import User; from core.models import Profile; \
    user, created = User.objects.get_or_create(username='dario', defaults={'email': 'dario@example.com', 'is_staff': True, 'is_superuser': True}); \
    if created: user.set_password('tuxx6393'); user.save(); Profile.objects.get_or_create(user=user, defaults={'role': 'editor'})" || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
