from django.urls import path

from . import views

# Create namespace, when indexing in .html files add base:{name}
app_name = "base"
urlpatterns = [
    path("", views.home, name="home"),
    path("detail/<int:pk>", views.detail, name="detail"),
    path("add", views.createItem, name="create_item"),
    path("update/<int:pk>", views.updateItem, name="update_item"),
    path("delete/<int:pk>", views.deleteItem, name="delete_item"),
]
