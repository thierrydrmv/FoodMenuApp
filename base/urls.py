from django.urls import path

from . import views

# Create namespace, when indexing in .html files add base:{name}
app_name = "base"
urlpatterns = [
    path("", views.home, name="home"),
    path("detail/<int:pk>", views.detail, name="detail"),
]
