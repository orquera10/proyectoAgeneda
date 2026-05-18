from django.db import migrations, models
from django.utils import timezone


def split_dia_horario(apps, schema_editor):
    EntradaAgenda = apps.get_model('agenda', 'EntradaAgenda')

    for entrada in EntradaAgenda.objects.exclude(dia_horario__isnull=True):
        dia_horario = timezone.localtime(entrada.dia_horario)
        entrada.fecha = dia_horario.date()
        entrada.horario = dia_horario.time().replace(second=0, microsecond=0)
        entrada.save(update_fields=['fecha', 'horario'])


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0005_alter_entradaagenda_direccion_coordinacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='entradaagenda',
            name='fecha',
            field=models.DateField(blank=True, null=True, verbose_name='fecha'),
        ),
        migrations.AddField(
            model_name='entradaagenda',
            name='horario',
            field=models.TimeField(blank=True, null=True, verbose_name='horario'),
        ),
        migrations.RunPython(split_dia_horario, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='entradaagenda',
            name='dia_horario',
        ),
        migrations.AlterModelOptions(
            name='entradaagenda',
            options={
                'ordering': ['mes', 'fecha', 'horario', 'nombre_actividad'],
                'verbose_name': 'entrada de agenda',
                'verbose_name_plural': 'entradas de agenda',
            },
        ),
    ]
