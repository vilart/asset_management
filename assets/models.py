from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# Create your models here.


class DeviceModel(models.Model):
    manufacturer = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.manufacturer} {self.name}"


class PurchaseOrder(models.Model):
    number = models.CharField(max_length=100, unique=True)
    supplier = models.CharField(max_length=150)
    order_date = models.DateField()

    def __str__(self):
        return f"PO: {self.number} ({self.supplier})"


class Asset(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        ACTIVE = "ACTIVE", "Active"
        IN_STOCK = "IN_STOCK", "In stock"
        IN_REPAIR = "IN_REPAIR", "In repair"
        SOLD = "SOLD", "Sold"
        SCRAPPED = "SCRAPPED", "Scrapped"

    serial_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)

    # Foreign keys
    device_model = models.ForeignKey(
        DeviceModel, on_delete=models.PROTECT, related_name="assets"
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )
    assigned_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets"
    )

    creation_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    additional_info = models.TextField(blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.device_model} - {self.name} ({self.serial_number})"
