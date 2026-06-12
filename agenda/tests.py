from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import EntradaAgenda


class AgendaListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lector', password='testpass123')
        self.client.force_login(self.user)

    def create_entrada(self, nombre, **kwargs):
        defaults = {
            'nombre_actividad': nombre,
            'creado_por': self.user,
            'mes': timezone.localdate().month,
        }
        defaults.update(kwargs)
        return EntradaAgenda.objects.create(**defaults)

    def test_shows_all_current_month_entries_without_pagination(self):
        hoy = timezone.localdate()

        for index in range(12):
            self.create_entrada(
                f'Entrada {index}',
                fecha=date(hoy.year, hoy.month, 1),
            )

        response = self.client.get(reverse('agenda_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['entradas']), 12)
        self.assertNotIn('page_obj', response.context)
        self.assertNotContains(response, 'pagination-nav')

    def test_filters_current_month_and_orders_by_date_with_completed_last(self):
        hoy = timezone.localdate()
        otro_mes = 12 if hoy.month == 1 else hoy.month - 1
        otro_mes_anio = hoy.year - 1 if hoy.month == 1 else hoy.year

        realizada_temprana = self.create_entrada(
            'Realizada temprana',
            fecha=date(hoy.year, hoy.month, 1),
            realizada=True,
        )
        pendiente_tardia = self.create_entrada(
            'Pendiente tardia',
            fecha=date(hoy.year, hoy.month, 10),
        )
        pendiente_temprana = self.create_entrada(
            'Pendiente temprana',
            fecha=date(hoy.year, hoy.month, 2),
        )
        sin_fecha = self.create_entrada(
            'Sin fecha exacta',
            fecha=None,
            mes=hoy.month,
        )
        self.create_entrada(
            'Otro mes',
            fecha=date(otro_mes_anio, otro_mes, 1),
            mes=otro_mes,
        )

        response = self.client.get(reverse('agenda_list'))

        self.assertEqual(
            list(response.context['entradas']),
            [pendiente_temprana, pendiente_tardia, sin_fecha, realizada_temprana],
        )
