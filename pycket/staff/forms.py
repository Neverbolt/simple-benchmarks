from django import forms
from shop.models import Event


class EventForm(forms.ModelForm):
    seating_upload = forms.FileField(required=False)

    class Meta:
        model = Event
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)

        upload = self.cleaned_data.get("seating_upload")
        if upload:
            instance.seating_plan = upload.read()
            print("uploaded")

        if commit:
            instance.save()

        return instance
