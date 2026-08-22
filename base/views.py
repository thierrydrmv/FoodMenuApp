from django.shortcuts import render

# Create your views here.
from .models import Item


def home(request):
    all_items = Item.objects.all()
    context = {"all_items": all_items}
    return render(request, "base/index.html", context)


def detail(request, pk):
    item = Item.objects.get(id=pk)
    context = {"item": item}
    return render(request, "base/detail.html", context)
