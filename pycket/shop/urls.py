from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('event/<int:event_id>', views.event, name='event'),
    path('tickets', views.tickets, name='tickets'),
    path('ticket/<int:ticket_id>', views.ticket, name='ticket'),
]
