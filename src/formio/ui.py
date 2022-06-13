from hypergen.template import *
from contextlib import contextmanager

@contextmanager
def card(title):
    with div(class_="card"):
        if title:
            h5(title, class_="card-header")
        with div(class_="card-body"):
            yield

@contextmanager
def form_group(form, name):
    with div(class_="form-group"):
        for error in form[name].errors:
            div(error, class_="alert alert-danger", role="alert")
        label(form[name].label)
        yield
