from django.core.management.base import BaseCommand
from django.utils import timezone

from agenda.models import EntradaAgenda


class Command(BaseCommand):
    help = 'Marca automáticamente como realizadas las tareas con fecha anterior a hoy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué tareas serían actualizadas sin hacer cambios',
        )

    def handle(self, *args, **kwargs):
        dry_run = kwargs['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== MODO SIMULACIÓN (dry-run) ==='))
            self.stdout.write(self.style.WARNING('No se realizarán cambios en la base de datos\n'))
        
        # Get today's date
        today = timezone.localdate()
        
        # Find all entries with fecha before today that are not marked as completed
        entradas_vencidas = EntradaAgenda.objects.filter(
            fecha__lt=today,
            realizada=False
        ).select_related('creado_por')
        
        count = entradas_vencidas.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No hay tareas vencidas pendientes.'))
            return
        
        self.stdout.write(f'Encontradas {count} tareas vencidas:\n')
        
        for entrada in entradas_vencidas:
            dias_vencida = (today - entrada.fecha).days if entrada.fecha else 'N/A'
            self.stdout.write(
                f"  - ID {entrada.id}: {entrada.nombre_actividad}\n"
                f"    Fecha: {entrada.fecha} (vencida hace {dias_vencida} días)\n"
                f"    Creada por: {entrada.creado_por.username}\n"
            )
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nEn modo dry-run, estas {count} tareas serían marcadas como realizadas.'
            ))
        else:
            # Update all entries
            updated_count = EntradaAgenda.marcar_vencidas_como_realizadas()
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ {updated_count} tareas fueron marcadas automáticamente como realizadas.'
            ))