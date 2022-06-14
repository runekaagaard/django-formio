import json

from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect

from hypergen.imports import *

from formio import templates
from formio.models import Builder, Submission
from formio.forms import builder_model_form

@liveview(re_path=r"^$", perm="formio.view_builder", base_template=templates.base_template())
def index(request):
    templates.index(Builder.objects.all())

@liveview(perm="formio.change_builder", path="edit/<int:pk>/", base_template=templates.base_template())
def edit(request, pk):
    builder = Builder.objects.get(pk=pk)
    command("hypergen.setClientState", "formio", {"form": builder.form})
    form = builder_model_form(data=None, instance=builder)
    templates.edit(form, builder.can_publish())

@liveview(perm="formio.add_builder", base_template=templates.base_template())
def add(request):
    form = builder_model_form()
    command("hypergen.setClientState", "formio", {"form": json.loads(form["form"].value())})
    templates.edit(form, False)

@action(perm="formio.change_builder", base_template=templates.base_template())
def save(request, data, publish):
    builder = Builder.objects.get(pk=data["pk"]) if data["pk"] else None
    form = builder_model_form(data=data, instance=builder)
    if not form.is_valid():
        command("hypergen.setClientState", "formio", {"form": json.loads(form["form"].value())})
        templates.edit(form, False)
    else:
        if publish is True:
            data2 = data
            data2["version"] += 1
            builder_form = json.loads(data2["form"])
            builder_form["versions"][data2["version"]] = builder_form["draft"]
            data2["form"] = json.dumps(builder_form)
            form2 = builder_model_form(data=data2, instance=builder)
            assert form2.is_valid()
            form2.save()
        else:
            form.save()

        return HttpResponseRedirect(edit.reverse(pk=form.instance.pk))

@liveview(perm="formio.add_submission", path="test/<int:pk>/<int:version>/",
          base_template=templates.base_template())
def test(request, /, *, pk, version):
    builder = Builder.objects.get(pk=pk)
    command("hypergen.setClientState", "formio", {"form": builder.form_at_version(version)})
    templates.test(builder.pk, builder.internal_title, version)

def submit_save(request, form_id, object_id, submission, version, content_type=None):
    builder = Builder.objects.get(pk=form_id)
    submission = Submission(
        added_by=request.user,
        builder=builder,
        builder_version=version,
        data=submission["data"],
        metadata=submission["metadata"],
        content_type=content_type,
        object_id=object_id,
    )
    submission.save()

@action(perm="formio.add_submission")
def submit_test(request, builder_id, object_id, submission, version):
    builder = Builder.objects.get(pk=builder_id)
    assert builder.version > 0 and builder.version == version
    submit_save(request, builder_id, object_id, submission, version,
                content_type=ContentType.objects.get_for_model(builder))
    return HttpResponseRedirect(user_submissions.reverse(builder_id))

@action(perm="formio.add_submission")
def submit(request, builder_id, object_id, submission):
    submit_save(request, builder_id, object_id, submission)

@liveview(path="history/<int:builder_id>/", perm="formio.view_builder", base_template=templates.base_template())
def history(request, /, *, builder_id):
    builder = Builder.objects.get(pk=builder_id)
    templates.history(builder)

@liveview(path="user_submissions/<int:builder_id>/", perm="formio.view_submission",
          base_template=templates.base_template())
def user_submissions(request, /, *, builder_id):
    builder = Builder.objects.get(pk=builder_id)
    submissions = Submission.objects.filter(builder_id=builder_id).order_by("-id")
    templates.user_submissions(builder, submissions)
