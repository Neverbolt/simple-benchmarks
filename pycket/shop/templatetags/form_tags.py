from django import template

register = template.Library()


@register.filter
def get_field(form, field_name):
    return form[field_name]


@register.filter
def get_field_id_for_label(form, field_name):
    return form[field_name].id_for_label
