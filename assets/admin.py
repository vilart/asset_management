from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import DeviceModel, PurchaseOrder, Asset

# Register your models here.


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ("manufacturer", "name")
    search_fields = ("manufactirer", "name")


@admin.register(PurchaseOrder)
class PurchaseModelAdmin(admin.ModelAdmin):
    list_display = ("number", "supplier", "order_date")
    search_fields = ("number", "supplier")


@admin.register(Asset)
class AssetAdmin(SimpleHistoryAdmin):
    list_display = ("serial_number", "name", "device_model", "status", "assigned_user")
    list_filter = ("status", "device_model")
    search_fields = ("serial_number", "name", "ip_address")
