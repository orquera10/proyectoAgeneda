from django.urls import path

from .views import agenda_create, agenda_list, agenda_toggle_realizada, agenda_update


urlpatterns = [
    path('', agenda_list, name='agenda_list'),
    path('nueva/', agenda_create, name='agenda_create'),
    path('<int:pk>/editar/', agenda_update, name='agenda_update'),
    path('<int:pk>/toggle-realizada/', agenda_toggle_realizada, name='agenda_toggle_realizada'),
]
