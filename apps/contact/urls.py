from django.urls import path

from .views import ContactFormView

app_name = "contact"

urlpatterns = [
    path("submit/", ContactFormView.as_view(), name="submit"),
]
