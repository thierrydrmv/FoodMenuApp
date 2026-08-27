from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .managers import ItemManager


# Create your models here.
class Item(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=("item_name", "item_description")),
        ]

    item_name = models.CharField(max_length=200, db_index=True)
    item_description = models.CharField()
    item_price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    item_image = models.URLField(
        max_length=500,
        default="https://www.runawayapricot.com/wp-content/uploads/2014/09/placeholder.jpg",
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # soft delete flag
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = ItemManager()

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1,  # type: ignore
    )

    def __str__(self):
        return f"{self.item_name}, price: {self.item_price} "

    def get_absolute_url(self):
        return reverse("base:home")

    def soft_delete(self, using=None, keep_parents=True):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


class Category(models.Model):
    name = models.CharField(max_length=100)
    added_on = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
