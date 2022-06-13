from hypergen.hypergen import autourls
from formio import views

app_name = 'formio'

# Automatically creates urlpatterns for all functions in views.py decorated with @liveview or @action.
urlpatterns = autourls(views, namespace=app_name)
