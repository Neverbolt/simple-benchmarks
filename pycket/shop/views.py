import time

from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.timezone import now

from shop.forms import SeatSelectionForm
from shop.models import Event, SeatingPlan, SeatReservation, Ticket


def index(request):
    events = Event.objects.filter(public=True, date__gt=now())
    return render(request, 'index.html', {'events': events})


@transaction.atomic
def event(request, event_id: int):
    try:
        e = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return redirect('home')

    import pickle
    seating_plan = pickle.loads(e.seating_plan)
    filled_seating_plan = seating_plan.with_reservations(e.seatreservation_set.all())

    if request.method == 'POST':
        form = SeatSelectionForm(filled_seating_plan.seating_grid, filled_seating_plan.stage_width, request.POST)
        if not form.is_valid():
            form.add_error(None, 'Invalid seat selection')
            return render(request, 'event.html', {'event': e, 'seating': form})

        if not filled_seating_plan.can_reserve(form.cleaned_data['seats']):
            form.add_error(None, 'Invalid seat selection')
            return render(request, 'event.html', {'event': e, 'seating': form})

        total = e.price * form.cleaned_data['num_seats']
        if request.user.customer.balance < total:
            form.add_error(None, 'Insufficient funds')
            return render(request, 'event.html', {'event': e, 'seating': form})

        reservations = [SeatReservation(event=e, row=row, number=number) for row, number in form.cleaned_data['seats']]
        for r in reservations:
            r.save()
        ticket = Ticket(customer=request.user.customer, event=e, total=total)
        ticket.save()
        ticket.seats.set(reservations)
        ticket.save()

        request.user.customer.balance -= total
        request.user.customer.save()

        return redirect('ticket', ticket.id)

    else:
        form = SeatSelectionForm(filled_seating_plan.seating_grid, filled_seating_plan.stage_width)

    if request.user.is_authenticated:
        tickets = Ticket.objects.filter(customer=request.user.customer, event=e).all()
    else:
        tickets = []

    return render(request, 'event.html', {'event': e, 'seating': form, 'tickets': tickets})


@login_required
def ticket(request, ticket_id: int):
    try:
        t = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return redirect('home')

    qr_content = Signer().sign(t.id)

    return render(request, 'ticket.html', {'ticket': t, 'qr_content': qr_content})


@login_required
def tickets(request):
    upcoming = Ticket.objects.filter(customer=request.user.customer, event__date__gt=now()).all()
    previous = Ticket.objects.filter(customer=request.user.customer, event__date__lt=now()).all()

    return render(request, 'tickets.html', {'upcoming': upcoming, 'previous': previous})

