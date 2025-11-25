import os

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from shop.models import Event

from .forms import EventForm


@staff_member_required
def home_staff(request):
    admin_flag = os.environ.get(
        "FLAG_ADMIN", "ADMIN FLAG NOT SET, THIS IS AN ISSUE IN THE TEST ENVIRONMENT!"
    )
    events = Event.objects.all()
    return render(
        request, "index_staff.html", {"events": events, "admin_flag": admin_flag}
    )


@staff_member_required
def new_event(request):
    return render(request, "new_event.html")


@method_decorator(staff_member_required, name="dispatch")
class EventEditView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = "event_edit.html"
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        return reverse("event", kwargs={"event_id": self.object.id})


@staff_member_required
def event_seating_plan(request, event_id):
    event = Event.objects.get(pk=event_id)
    if not event.seating_plan:
        raise HttpResponseNotFound("No attachment")

    resp = HttpResponse(event.seating_plan, content_type="application/octet-stream")
    resp["Content-Disposition"] = f'attachment; filename="{event.id}_seating_plan.bin"'
    return resp
