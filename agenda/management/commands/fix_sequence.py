from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequence for agenda_entradaagenda table'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fixing sequence for agenda_entradaagenda table...')
        
        with connection.cursor() as cursor:
            # Get the current maximum ID from the table
            cursor.execute('SELECT MAX(id) FROM agenda_entradaagenda')
            result = cursor.fetchone()
            max_id = result[0] if result[0] is not None else 0
            
            # Get the current sequence value
            cursor.execute("SELECT last_value FROM agenda_entradaagenda_id_seq")
            seq_result = cursor.fetchone()
            current_seq = seq_result[0]
            
            self.stdout.write(f'Current max ID: {max_id}')
            self.stdout.write(f'Current sequence value: {current_seq}')
            
            if max_id >= current_seq:
                # Set sequence to max_id + 1
                new_seq_value = max_id + 1
                cursor.execute(f"SELECT setval('agenda_entradaagenda_id_seq', {new_seq_value})")
                self.stdout.write(
                    self.style.SUCCESS(f'Sequence updated to {new_seq_value}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Sequence is already ahead of max ID, no action needed.')
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed the sequence!'))