from django.urls import path

from . import views

urlpatterns = [
    path("event/new/", views.new_event, name="new_event"),
    path("event/<int:event_id>/edit", views.EventEditView.as_view(), name="edit_event"),
    path(
        "event/<int:event_id>/seating_plan",
        views.event_seating_plan,
        name="event_seating_plan",
    ),
    path("staff/", views.home_staff, name="home_staff"),
]
