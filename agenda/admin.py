from django.contrib import admin

from .models import EntradaAgenda


@admin.register(EntradaAgenda)
class EntradaAgendaAdmin(admin.ModelAdmin):
    list_display = (
        'mes',
        'fecha',
        'horario_inicio',
        'horario_fin',
        'nombre_actividad',
        'localidad',
        'prioridad_actividad',
        'creado_por',
    )
    list_filter = ('mes', 'prioridad_actividad', 'localidad', 'fecha')
    search_fields = (
        'nombre_actividad',
        'direccion_coordinacion',
        'localidad',
        'lugar_actividad',
        'poblacion_destinataria',
        'objetivo',
    )
