from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm

# Create your views here.
from .models import Item


def home(request):
    all_items = Item.objects.all()
    context = {"all_items": all_items}
    return render(request, "base/index.html", context)


def detail(request, pk):
    item = get_object_or_404(Item, id=pk)
    context = {"item": item}
    return render(request, "base/detail.html", context)


def createItem(request):
    form = ItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("base:home")
    context = {"form": form}
    return render(request, "base/item_form.html", context)


def updateItem(request, pk):
    item = get_object_or_404(Item, id=pk)
    form = ItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect("base:home")
    context = {"form": form}
    return render(request, "base/item_form.html", context)


def deleteItem(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == "POST":
        item.delete()
        return redirect("base:home")
    return render(request, "base/item_delete.html")
