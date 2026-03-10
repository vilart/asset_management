from django import forms
from .models import Asset, DeviceModel, PurchaseOrder


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "serial_number",
            "name",
            "device_model",
            "purchase_order",
            "assigned_user",
            "status",
            "additional_info",
        ]
        widgets = {
            "serial_number": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "device_model": forms.Select(attrs={"class": "form-select"}),
            "purchase_order": forms.Select(attrs={"class": "form-select"}),
            "assigned_user": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "additional_info": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }


class DeviceModelForm(forms.ModelForm):
    class Meta:
        model = DeviceModel
        fields = ["manufacturer", "name"]
        widgets = {
            "manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ["number", "supplier", "order_date"]
        widgets = {
            "number": forms.TextInput(attrs={"class": "form-control"}),
            "supplier": forms.TextInput(attrs={"class": "form-control"}),
            "order_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
