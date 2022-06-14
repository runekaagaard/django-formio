window.formio = {}
var formio = window.formio

formio.builder_value_func = function () {
  var value = hypergen.clientState.formio.form
  value.draft = formio.builder.form
  return JSON.stringify(value)
}

formio.init_builder = function(id) {
  hypergen.ready(function() {
    Formio.builder(document.getElementById(id), hypergen.clientState.formio.form.draft)
          .then(builder => {
            formio.builder = builder
          })
  }, {partial: true})
}

formio.init_form_display = function(id, url, form_id, object_id, version) {
  hypergen.ready(function() {
    Formio.createForm(document.getElementById('formio'), hypergen.clientState.formio.form)
      .then(function(form) {
          form.nosubmit = true
          form.on('submit', function(submission) {
              hypergen.callback(url, [form_id, object_id, submission, version])
          })
      })
  }, {partial: true})
}
