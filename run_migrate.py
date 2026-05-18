import os
import sys
import django
from decouple import config

# Guardar configuración original
original_env = {
    'DB_NAME': os.environ.get('DB_NAME', ''),
    'DB_USER': os.environ.get('DB_USER', ''),
    'DB_PASSWORD': os.environ.get('DB_PASSWORD', ''),
    'DB_HOST': os.environ.get('DB_HOST', ''),
    'DB_PORT': os.environ.get('DB_PORT', ''),
}

# Configurar Django para usar SQLite temporalmente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Forzar configuración SQLite para lectura
os.environ['DB_NAME'] = 'db.sqlite3'
os.environ['DB_USER'] = ''
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = ''
os.environ['DB_PORT'] = ''

django.setup()

from django.core.management import call_command

print("=" * 60)
print("Migración de SQLite a PostgreSQL")
print("=" * 60)

# Paso 1: Hacer dump de los datos de SQLite
print("\n[1/4] Exportando datos desde SQLite...")
try:
    with open('sqlite_data.json', 'w', encoding='utf-8') as f:
        call_command('dumpdata', '--natural-foreign', '--natural-primary', 
                     '--exclude', 'auth.Permission', '--exclude', 'contenttypes', 
                     stdout=f)
    print("✓ Datos exportados a sqlite_data.json")
except Exception as e:
    print(f"✗ Error al exportar datos: {e}")
    sys.exit(1)

# Paso 2: Cambiar a PostgreSQL
print("\n[2/4] Cambiando configuración a PostgreSQL...")
os.environ['DB_NAME'] = config('DB_NAME', default='agenda_db')
os.environ['DB_USER'] = config('DB_USER', default='postgres')
os.environ['DB_PASSWORD'] = config('DB_PASSWORD', default='')
os.environ['DB_HOST'] = config('DB_HOST', default='localhost')
os.environ['DB_PORT'] = config('DB_PORT', default='5432')
print(f"✓ Configurado para conectar a PostgreSQL: {os.environ['DB_NAME']}@{os.environ['DB_HOST']}")

# Necesario recargar la configuración de Django
from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.environ['DB_NAME'],
    'USER': os.environ['DB_USER'],
    'PASSWORD': os.environ['DB_PASSWORD'],
    'HOST': os.environ['DB_HOST'],
    'PORT': os.environ['DB_PORT'],
}

# Paso 3: Cargar datos en PostgreSQL
print("\n[3/4] Importando datos a PostgreSQL...")
try:
    call_command('loaddata', 'sqlite_data.json')
    print("✓ Datos importados correctamente")
except Exception as e:
    print(f"✗ Error al importar datos: {e}")
    sys.exit(1)

# Limpieza
print("\n" + "=" * 60)
print("¡Migración completada exitosamente!")
print("=" * 60)