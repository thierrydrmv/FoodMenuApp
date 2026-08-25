from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.
class Item(models.Model):
    def __str__(self):
        return self.item_name

    item_name = models.CharField(max_length=200)
    item_description = models.CharField()
    item_price = models.IntegerField()
    item_image = models.CharField(
        max_length=500,
        default="https://www.runawayapricot.com/wp-content/uploads/2014/09/placeholder.jpg",
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1,
    )

    def get_absolute_url(self):
        return reverse("base:home")
