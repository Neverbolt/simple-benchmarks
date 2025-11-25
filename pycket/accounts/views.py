from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import RedirectURLMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import FormView
from shop.models import Customer

from accounts.forms import UserCreationForm, UserForm


class RegisterView(RedirectURLMixin, FormView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    next_page = "home"

    def form_valid(self, form):
        user = form.save()
        Customer.objects.create(user=user, balance=5.00)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())


@login_required
def profile(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            # Redirect to a new URL:
            return redirect("profile")

    else:
        form = UserForm(instance=request.user)

    return render(request, "registration/profile.html", {"form": form})
