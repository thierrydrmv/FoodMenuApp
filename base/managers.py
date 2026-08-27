from django.db import models


class ItemManager(models.Manager):
    def cheap_items(self):
        return self.filter(item_price__lt=2)

    def expensive_items(self):
        return self.filter(item_price__gt=10)

    def search(self, keyword):
        return self.filter(item_name__icontains=keyword)
