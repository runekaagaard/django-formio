from django.forms.models import modelform_factory

from formio.models import Builder

def builder_model_form(data=None, instance=None):
    return modelform_factory(
        Builder, fields=["internal_title", "internal_description", "content_type", "version", "form",
                         "version"])(data=data, instance=instance)
