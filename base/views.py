from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm

# Create your views here.
from .models import Item


@login_required
def home(request):
    all_items = Item.objects.all()
    context = {"all_items": all_items}
    return render(request, "base/index.html", context)


@login_required
def detail(request, pk):
    item = get_object_or_404(Item, id=pk)
    context = {"item": item}
    return render(request, "base/detail.html", context)


@login_required
def createItem(request):
    form = ItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("base:home")
    context = {"form": form}
    return render(request, "base/item_form.html", context)


@login_required
def updateItem(request, pk):
    item = get_object_or_404(Item, id=pk)
    form = ItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect("base:home")
    context = {"form": form}
    return render(request, "base/item_form.html", context)


@login_required
def deleteItem(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == "POST":
        item.delete()
        return redirect("base:home")
    return render(request, "base/item_delete.html")
