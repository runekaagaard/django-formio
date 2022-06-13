from django.db import models as m
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

def builder_form_default():
    return {"draft": {}, "versions": {}}

class Builder(m.Model):
    internal_title = m.CharField(max_length=80)
    internal_description = m.TextField(blank=True)
    content_type = m.ForeignKey(ContentType, on_delete=m.PROTECT)
    form = m.JSONField(default=builder_form_default)
    version = m.PositiveIntegerField(default=0)

    def __str__(self):
        return self.internal_title

    def components(self):
        return {
            x["key"]: x for y in self.form["versions"].values() for x in y["components"] if x["key"] != "submit"
        }

    def can_publish(self):
        version = str(self.version)
        if self.pk is None:
            return False
        elif not self.form["draft"]:
            return False
        elif version not in self.form["versions"]:
            return True
        else:
            return self.form["draft"] != self.form["versions"][version]

    def form_at_version(self, version):
        return self.form["versions"][str(version)]

class Submission(m.Model):
    added = m.DateTimeField(auto_now_add=True)
    added_by = m.ForeignKey("auth.User", on_delete=m.CASCADE)
    builder = m.ForeignKey("formio.Builder", on_delete=m.PROTECT)
    builder_version = m.PositiveIntegerField()
    data = m.JSONField()
    metadata = m.JSONField(null=True, default=None)
    content_type = m.ForeignKey(ContentType, on_delete=m.PROTECT)
    object_id = m.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
