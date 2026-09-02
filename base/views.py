import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# from django.views.decorators.cache import cache_page
# from django.views.decorators.vary import vary_on_headers
# from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from rest_framework import generics

from base.forms import ItemForm

# Create your views here.
from .models import Item
from .serializers import ItemSerializer

logger = logging.getLogger(__name__)

# ----------------------------- CRUD Using generic views ---------------------------


class ItemListCreateAPI(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


# ----------------------------- CRUD Using class-based views ---------------------------


# class ItemListCreateAPIView(APIView):
#     def get(self, request):
#         items = Item.objects.all()
#         serializer = ItemSerializer(items, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ItemSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class ItemDetailAPI(APIView):
#     def get_object(self, pk):
#         try:
#             return Item.objects.get(pk=pk)
#         except Item.DoesNotExist:
#             return None

#     def get(self, request, pk):
#         item = self.get_object(pk)
#         if not item:
#             return Response({"Error": "Item not found."})
#         serializer = ItemSerializer(item)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         item = self.get_object(pk)
#         if not item:
#             return Response({"Error": "Item not found."})
#         serializer = ItemSerializer(item, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def delete(self, request, pk):
#         item = self.get_object(pk)
#         if not item:
#             return Response({"Error": "Item not found."})
#         item.delete()
#         return Response({"message": f"Item {item.item_name} deleted.", "status": 204})


# ----------------------------- CRUD Using function-based views ---------------------------

# @api_view(["GET", "POST"])
# def item_list_create_api(request):
#     if request.method == "GET":
#         items = Item.objects.all()
#         serializer = ItemSerializer(items, many=True)
#         return Response(serializer.data)

#     serializer = ItemSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response(serializer.data, status=201)

# @api_view(["GET", "PUT", "DELETE"])
# def item_detail_api(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#     if request.method == "GET":
#         serializer = ItemSerializer(item)
#         return Response(serializer.data)
#     if request.method == "PUT":
#         serializer = ItemSerializer(item, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     item.delete()
#     return Response({"message": f"Item {item.item_name} deleted.", "status": 204})


# ----------------------------- APP ---------------------------


@login_required
# @cache_page(60 * 15)  # 15 minutes view level
# @vary_on_headers("User_Agent")  # cache at headers level, vary according to the user
def home(request):
    logger.info("Fetching all items from the database")
    logger.info(
        f"[{timezone.now().isoformat()}] User {request.user} request item list from ip: {request.META.get('REMOTE_ADDR')}"
    )
    all_items = Item.objects.all()
    logger.debug(f"Found {all_items.count()} items.")
    paginator = Paginator(all_items, per_page=5)
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)
    context = {"page_object": page_object}
    return render(request, "base/home.html", context)


# class base view is a easier and faster way to create generic views without
# additional logic.
# class HomeClassView(LoginRequiredMixin, ListView):
#     model = Item
#     template_name = "base/home.html"
#     context_object_name = "all_items"
#     login_url = "users/login"


@login_required
def detail(request, pk):
    logger.info(f"Fetching a specific item in the database id: {pk}.")
    item = get_object_or_404(Item, id=pk)
    logger.debug(f"Found {item.item_name}, Price: ${item.item_price}")
    context = {"item": item}
    return render(request, "base/detail.html", context)


# class DetailClassView(LoginRequiredMixin, DetailView):
#     model = Item
#     template_name = "base/detail.html"
#     context_object_name = "item"
#     login_url = "users/login"


@login_required
def createItem(request):
    form = ItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("base:home")

    context = {"form": form}
    return render(request, "base/item_form.html", context)


# have to pass the get_absolute url in the model
# class ItemCreateView(LoginRequiredMixin, CreateView):
#     model = Item
#     fields = ("item_name", "item_description", "item_price", "item_image")
#     template_name = "base/item_form.html"
#     login_url = "users/login"

#     def form_valid(self, form):
#         form.instance.creator = self.request.user
#         return super().form_valid(form)


# @login_required
# def updateItem(request, pk):
#     item = get_object_or_404(Item, id=pk)
#     form = ItemForm(request.POST or None, instance=item)
#     if form.is_valid():
#         form.save()
#         return redirect("base:home")
#     context = {"form": form}
#     return render(request, "base/item_form.html", context)


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ("item_name", "item_description", "item_price", "item_image")
    template_name = "base/item_form.html"
    login_url = "users/login"

    def get_queryset(self):
        return Item.objects.filter(creator=self.request.user)


@login_required
def deleteItem(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == "POST":
        item.soft_delete()
        return redirect("base:home")
    return render(request, "base/item_delete.html")


# class ItemDeleteView(LoginRequiredMixin, DeleteView):
#     model = Item
#     template_name = "base/item_delete.html"
#     login_url = "users/login"
#     success_url = reverse_lazy("base:home")
