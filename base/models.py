from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.
class Item(models.Model):
    item_name = models.CharField(max_length=200)
    item_description = models.CharField()
    item_price = models.DecimalField(max_digits=6, decimal_places=2)
    item_image = models.URLField(
        max_length=500,
        default="https://www.runawayapricot.com/wp-content/uploads/2014/09/placeholder.jpg",
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1,  # type: ignore
    )

    def get_absolute_url(self):
        return reverse("base:home")

    def __str__(self):
        return f"{self.item_name}, price: {self.item_price} "


class Category(models.Model):
    name = models.CharField(max_length=100)
    added_on = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
