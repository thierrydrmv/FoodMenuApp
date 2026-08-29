from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

# Create your views here.
from .models import Item


@login_required
def home(request):
    all_items = Item.objects.all()
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


# @login_required
# def detail(request, pk):
#     item = get_object_or_404(Item, id=pk)
#     context = {"item": item}
#     return render(request, "base/detail.html", context)


class DetailClassView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = "base/detail.html"
    context_object_name = "item"
    login_url = "users/login"


# @login_required
# def createItem(request):
#     form = ItemForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         form.save()
#         return redirect("base:home")
#     context = {"form": form}
#     return render(request, "base/item_form.html", context)


# have to pass the get_absolute url in the model
class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ("item_name", "item_description", "item_price", "item_image")
    template_name = "base/item_form.html"
    login_url = "users/login"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


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
