from django import forms

from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("item_name", "item_description", "item_price", "item_image")
        widgets = {  # noqa: RUF012
            "item_name": forms.TextInput(
                attrs={"placeholder": "eg Margherita Pizza", "required": True}
            ),
            "item_description": forms.TextInput(
                attrs={"placeholder": "eg Cheesy", "required": True}
            ),
            "item_price": forms.NumberInput(
                attrs={"placeholder": "100", "required": True}
            ),
            "item_image": forms.URLInput(
                attrs={"placeholder": "https://google.com", "required": False}
            ),
        }

    def clean_item_price(self):
        price = self.cleaned_data["item_price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return price

    def clean(self):
        cleaned = super().clean()
        name = cleaned.get("item_name")
        description = cleaned.get("item_description")
        if name and description and name.lower() in description.lower():
            self.add_error(
                "item_description", "Description should add new info beyond the name."
            )
        return cleaned
