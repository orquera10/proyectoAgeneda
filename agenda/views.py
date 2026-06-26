from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from core.models import Profile

from .forms import EntradaAgendaForm
from .models import EntradaAgenda


def is_editor(user):
    try:
        return user.is_authenticated and user.profile.role == Profile.Role.EDITOR
    except (AttributeError, Profile.DoesNotExist):
        return False


def is_staff(user):
    return user.is_authenticated and user.is_staff


@login_required
def agenda_list(request):
    hoy = timezone.localdate()
    try:
        selected_mes = int(request.GET.get('mes', hoy.month))
    except (TypeError, ValueError):
        selected_mes = hoy.month

    if selected_mes not in EntradaAgenda.Mes.values:
        selected_mes = hoy.month

    entradas = (
        EntradaAgenda.objects.select_related('creado_por')
        .filter(
            Q(fecha__year=hoy.year, fecha__month=selected_mes)
            | Q(fecha__isnull=True, mes=selected_mes)
        )
        .order_by(
            'realizada',
            F('fecha').asc(nulls_last=True),
            F('horario_inicio').asc(nulls_last=True),
            'id',
        )
    )

    return render(
        request,
        'agenda/agenda_list.html',
        {
            'entradas': entradas,
            'can_create': is_editor(request.user),
            'can_delete': is_staff(request.user),
            'month_choices': EntradaAgenda.Mes.choices,
            'selected_mes': selected_mes,
        },
    )


@login_required
@user_passes_test(is_editor, login_url='dashboard')
def agenda_create(request):
    if request.method == 'POST':
        form = EntradaAgendaForm(request.POST, is_editor=True)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.creado_por = request.user
            entrada.save()
            messages.success(request, 'La entrada fue agregada a la agenda.')
            return redirect('agenda_list')
    else:
        form = EntradaAgendaForm(is_editor=True)

    return render(
        request,
        'agenda/agenda_form.html',
        {
            'form': form,
            'title': 'Nueva entrada de agenda',
            'submit_label': 'Guardar entrada',
        },
    )


@login_required
@user_passes_test(is_editor, login_url='dashboard')
def agenda_update(request, pk):
    entrada = get_object_or_404(EntradaAgenda, pk=pk)

    if request.method == 'POST':
        form = EntradaAgendaForm(request.POST, instance=entrada, is_editor=True)
        if form.is_valid():
            form.save()
            messages.success(request, 'La entrada fue actualizada.')
            return redirect('agenda_list')
    else:
        form = EntradaAgendaForm(instance=entrada, is_editor=True)

    return render(
        request,
        'agenda/agenda_form.html',
        {
            'form': form,
            'entrada': entrada,
            'title': 'Editar entrada de agenda',
            'submit_label': 'Guardar cambios',
        },
    )


@login_required
@user_passes_test(is_editor, login_url='dashboard')
def agenda_toggle_realizada(request, pk):
    """Toggle the 'realizada' status of an agenda entry."""
    entrada = get_object_or_404(EntradaAgenda, pk=pk)
    
    # Toggle the status
    entrada.realizada = not entrada.realizada
    entrada.save()
    
    # Set message based on new status
    if entrada.realizada:
        messages.success(request, 'La entrada fue marcada como realizada.')
    else:
        messages.success(request, 'La entrada fue marcada como pendiente.')
    
    next_url = request.POST.get('next') or 'agenda_list'
    return redirect(next_url)


@login_required
@user_passes_test(is_staff, login_url='dashboard')
@require_POST
def agenda_delete(request, pk):
    entrada = get_object_or_404(EntradaAgenda, pk=pk)
    entrada.delete()
    messages.success(request, 'La entrada fue eliminada.')

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect('agenda_list')
