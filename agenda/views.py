from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Profile

from .forms import EntradaAgendaForm
from .models import EntradaAgenda


def is_editor(user):
    return (
        user.is_authenticated
        and getattr(getattr(user, 'profile', None), 'role', None) == Profile.Role.EDITOR
    )


@login_required
def agenda_list(request):
    # Order by realizada (non-completed first), then by date and id
    entradas_list = EntradaAgenda.objects.select_related('creado_por').order_by('realizada', '-fecha', '-id')
    paginator = Paginator(entradas_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'agenda/agenda_list.html',
        {
            'entradas': page_obj,
            'page_obj': page_obj,
            'can_create': is_editor(request.user),
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
    
    return redirect('agenda_list')
