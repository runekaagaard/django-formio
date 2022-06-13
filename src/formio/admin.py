import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from formio.models import *

def display_json(data):
    return mark_safe("<pre><code>{}</code></pre>".format(json.dumps(data, indent=4)))

class BuilderAdmin(admin.ModelAdmin):
    list_display = ["pk", "internal_title", "content_type", "version"]
    fields = ["internal_title", "internal_description", "content_type", "version", "display_form"]
    readonly_fields = ["display_form"]

    def display_form(self, builder):
        return display_json(builder.form)

admin.site.register(Builder, BuilderAdmin)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["id", "builder", "content_type", "object_id", "content_object", "data"]
    list_filter = ["builder"]
    fields = [
        "added", "added_by", "display_data", "display_metadata", "object_id", "content_type", "content_object",
        "builder", "builder_version"
    ]
    readonly_fields = [
        "added", "added_by", "display_data", "display_metadata", "object_id", "content_type", "builder",
        "builder_version", "content_object"
    ]

    def display_data(self, submission):
        return display_json(submission.data)

    def display_metadata(self, submission):
        return display_json(submission.metadata)

admin.site.register(Submission, SubmissionAdmin)
