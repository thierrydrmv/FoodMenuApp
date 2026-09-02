from django.urls import path

# from django.views.decorators.cache import cache_page  # url level
from . import views

# Create namespace, when indexing in .html files add base:{name}
app_name = "base"
urlpatterns = [
    # URL API Patterns
    # path("api/items", views.item_list_create_api),
    path("api/items", views.ItemListCreateAPI.as_view()),
    # path("api/items/<int:pk>", views.item_detail_api),
    path("api/items/<int:pk>", views.ItemRetrieveUpdateDestroyAPI.as_view()),
    # path("", views.HomeClassView.as_view(), name="home"),
    # path("", cache_page(60 * 15)(views.home), name="home"),
    path("", views.home, name="home"),
    # path("detail/<int:pk>", views.DetailClassView.as_view(), name="detail"),
    path("detail/<int:pk>", views.detail, name="detail"),
    # path("add", views.ItemCreateView.as_view(), name="create_item"),
    path("add", views.createItem, name="create_item"),
    path("update/<int:pk>", views.ItemUpdateView.as_view(), name="update_item"),
    # path("update/<int:pk>", views.updateItem, name="update_item"),
    # path("delete/<int:pk>", views.ItemDeleteView.as_view(), name="delete_item"),
    path("delete/<int:pk>", views.deleteItem, name="delete_item"),
]
