from contextlib import contextmanager

d = dict

from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static

from hypergen.template import *
from hypergen.liveview import *
from hypergen.context import context
from hypergen.hypergen import compare_funcs

from formio.ui import *

def formio_head():
    script(src="https://cdn.form.io/formiojs/formio.full.min.js")
    script(src=static("formio/formio.js"))
    link(static("formio/formio.css"))
    link("https://cdn.form.io/formiojs/formio.full.min.css")
    link("https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css")
    link("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css")

def base_template(extra_head=None):
    @contextmanager
    def _base_template():
        from formio import views
        doctype()
        with html():
            with head():
                title("Formio")
                formio_head()

                if extra_head:
                    extra_head()
            with body():
                with nav(class_="navbar navbar-expand-lg navbar-light bg-light"):
                    with div(class_="collapse navbar-collapse"):
                        with ul(class_="navbar-nav"):
                            li(a("Builders", class_="nav-link", href=views.index.reverse()),
                               class_="nav-item active")

                with div(id="content", class_="container", style=d(padding_top="20px;")):
                    yield

    _base_template.target_id = "content"

    return _base_template

def builder_links(builder_id, version):
    from formio import views
    yield "Edit", views.edit, views.edit.reverse(pk=builder_id)
    if version > 0:
        yield "Test", views.test, views.test.reverse(pk=builder_id, version=version)
        yield "Submissions", views.user_submissions, views.user_submissions.reverse(builder_id=builder_id)

def index(builders):
    from formio import views
    p(a("Add new builder", href=views.add.reverse(), class_="btn btn-primary"), style=d(text_align="right"))
    if not builders:
        p("No builders yet, you should add one :)")
        return

    with table(class_="table table-bordered"):
        thead(tr(th("Id"), th("Internal titel", colspan=4)))
        tbody(
            tr(td(x.pk), td(x.internal_title), (td(a(title, href=href))
                                                for title, _, href in builder_links(x.pk, x.version)))
            for x in builders)

def builder_nav(builder_id, internal_title, version):
    from formio import views

    h1(internal_title)
    p("Showing builder at version ", version, class_="text-muted")

    ul((li(
        a(title, href=url,
          class_="nav-link active" if compare_funcs(context.request.resolver_match.func, view) else "nav-link"),
        class_="nav-item") for title, view, url in builder_links(builder_id, version)), class_="nav nav-tabs")

def edit(form, can_publish):
    from formio import views

    if form.instance.pk is not None:
        builder_nav(form.instance.pk, form["internal_title"].value(), form.instance.version)
    else:
        h2("Add new builder")

    with card("About this builder"):
        with form_group(form, "internal_title"):
            internal_title = input_(id="internal_title", class_="form-control",
                                    value=form["internal_title"].value())
        with form_group(form, "internal_description"):
            internal_description = textarea(
                form["internal_description"].value(),
                id="internal_description",
                class_="form-control",
            )
        with form_group(form, "content_type"):
            content_type = select((option(x.app_label, ".", x.model, " (", x.name, ")", value=x.pk, selected=x.pk
                                          == form["content_type"].value()) for x in ContentType.objects.all()),
                                  id="content_type", class_="form-control", coerce_to=int)

        builder_form = input_(type="hidden", id="data", js_value_func="formio.builder_value_func")
        version = input_(type="hidden", id="version", value=form["version"].value(), coerce_to=int)

        post_data = d(pk=form.instance.pk, internal_title=internal_title,
                      internal_description=internal_description, content_type=content_type, form=builder_form,
                      version=version)

        button("Save draft", id="save_draft", class_="btn btn-success mr-1",
               onclick=callback(views.save, post_data, False))

        if can_publish:
            button(
                "Publish", id="publish", class_="btn btn-danger",
                onclick=callback(views.save, post_data, True,
                                 confirm_="Are you sure that you want to publish a new version of this builder?"))

    with card("Form Configuration"):
        div(id="builder")

    command("formio.init_builder", "builder")

def test(pk, internal_title, version):
    from formio import views
    builder_nav(pk, internal_title, version)

    with card(None):
        div(id="formio")
    command("formio.init_form_display", "formio", views.submit_test.reverse(), pk, pk, version)

def display(form_id, object_id):
    from formio import views
    doctype()
    with html(lang="da"):
        with head():
            meta(charset="utf-8")
            meta(name="viewport", content="width=device-width, initial-scale=1")
            formio_head()
        with body():
            with div(style=d(padding="10px;")):
                div(id="formio")
            command("formio.init_form_display", "formio", views.submit.reverse(), form_id, object_id)

def user_submissions(builder, submissions):
    builder_nav(builder.pk, builder.internal_title, builder.version)

    if not submissions:
        p("This builder doesn't yet have any submissions.")
        return

    p("Showing", len(submissions), "user submissions", sep=" ", end=".")

    components = builder.components()
    with table(class_="table table-bordered table-striped"):
        with thead(), tr():
            th("Id")
            th("Builder Version")
            th("Added By")
            th("Time")
            th("Related Object")
            for k in components.keys():
                th(components[k]["label"])
        with tbody():
            for submission in submissions:
                tr(
                    (th(x) for x in (
                        submission.pk,
                        submission.builder_version,
                        submission.added_by,
                        span(str(submission.added)[:-7], class_="nowrap"),
                        span(submission.content_type, "(", submission.object_id, ")", ": ",
                             submission.content_object),
                    )),
                    (th(submission.data[k] if k in submission.data else "") for k in components.keys()),
                )
