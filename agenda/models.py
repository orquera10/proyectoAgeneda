from django.db import models
from django.conf import settings
from django.utils import timezone


def current_month():
    return timezone.localdate().month


class EntradaAgenda(models.Model):
    class Mes(models.IntegerChoices):
        ENERO = 1, 'Enero'
        FEBRERO = 2, 'Febrero'
        MARZO = 3, 'Marzo'
        ABRIL = 4, 'Abril'
        MAYO = 5, 'Mayo'
        JUNIO = 6, 'Junio'
        JULIO = 7, 'Julio'
        AGOSTO = 8, 'Agosto'
        SEPTIEMBRE = 9, 'Septiembre'
        OCTUBRE = 10, 'Octubre'
        NOVIEMBRE = 11, 'Noviembre'
        DICIEMBRE = 12, 'Diciembre'

    class Prioridad(models.TextChoices):
        ALTA = 'alta', 'Alta'
        MEDIA = 'media', 'Media'
        BAJA = 'baja', 'Baja'

    mes = models.PositiveSmallIntegerField(choices=Mes.choices, default=current_month, blank=True, null=True)
    fecha = models.DateField('fecha', blank=True, null=True)
    horario_inicio = models.TimeField('horario inicio', blank=True, null=True)
    horario_fin = models.TimeField('horario fin', blank=True, null=True)
    nombre_actividad = models.TextField('nombre de la actividad')
    direccion_coordinacion = models.CharField('direccion y/o coordinacion', max_length=255, blank=True)
    localidad = models.CharField(max_length=120, blank=True)
    lugar_actividad = models.CharField(
        'direccion / lugar en el que se desarrollara la actividad',
        max_length=255,
        blank=True,
    )
    poblacion_destinataria = models.CharField('poblacion destinataria', max_length=200, blank=True)
    objetivo = models.TextField(blank=True)
    prioridad_actividad = models.CharField(
        'prioridad de la actividad',
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
        blank=True,
    )
    requerimientos_comunicacion = models.TextField(
        'requerimientos especificos de comunicacion',
        blank=True,
        help_text='Piezas graficas, ceremonial, gacetilla, etc.',
    )
    informacion_brindada = models.TextField('informacion brindada', blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='entradas_agenda',
    )
    realizada = models.BooleanField(
        'realizada',
        default=False,
        help_text='Marcar como realizada para disminuir su prioridad en la visualización.',
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    @classmethod
    def marcar_vencidas_como_realizadas(cls):
        """Marcar como realizadas las entradas cuya fecha es anterior a hoy."""
        hoy = timezone.localdate()
        return cls.objects.filter(
            fecha__lt=hoy,
            realizada=False,
        ).update(realizada=True, actualizado=timezone.now())

    class Meta:
        ordering = ['realizada', '-fecha', '-id']
        verbose_name = 'entrada de agenda'
        verbose_name_plural = 'entradas de agenda'

    def __str__(self):
        if self.fecha and self.horario_inicio:
            fecha = f'{self.fecha:%d/%m/%Y} {self.horario_inicio:%H:%M}'
        elif self.fecha:
            fecha = f'{self.fecha:%d/%m/%Y} - horario a definir'
        else:
            fecha = f'{self.get_mes_display()} - fecha a definir'

        return f'{self.nombre_actividad} - {fecha}'
