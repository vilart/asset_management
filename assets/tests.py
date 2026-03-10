from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Asset, DeviceModel, PurchaseOrder
from django.contrib.auth.models import User

# Create your tests here.


class ModelsTests(TestCase):
    def test_device_model_str(self):
        """Test metody __str__ dla modelu DeviceModel"""
        model = DeviceModel.objects.create(manufacturer="Dell", name="XPS 15")
        self.assertEqual(str(model), "Dell XPS 15")

    def test_purchase_order_str(self):
        """Test metody __str__ dla modelu PurchaseOrder"""
        po = PurchaseOrder.objects.create(
            number="PO-123", supplier="Amazon", order_date=timezone.now().date()
        )
        self.assertEqual(str(po), "PO: PO-123 (Amazon)")

    def test_asset_str(self):
        """Test metody __str__ dla modelu Asset"""
        model = DeviceModel.objects.create(manufacturer="Dell", name="XPS 15")
        asset = Asset.objects.create(
            serial_number="SN123", name="PC-01", device_model=model
        )
        self.assertEqual(str(asset), "Dell XPS 15 - PC-01 (SN123)")


class AssetCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")
        self.client.force_login(self.user)
        self.device_model = DeviceModel.objects.create(
            manufacturer="Dell", name="Latitude 5520"
        )

    def test_create_asset_success(self):
        """Test czy jest poprawnie tworzony nowy sprzet"""
        self.assertEqual(Asset.objects.count(), 0)

        form_data = {
            "serial_number": "XYZ12345",
            "name": "PC-IT-001",
            "device_model": self.device_model.id,
            "status": "ACTIVE",
        }

        response = self.client.post(reverse("asset_create"), data=form_data)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Asset.objects.count(), 1)

        nowy_sprzet = Asset.objects.first()
        self.assertEqual(nowy_sprzet.serial_number, "XYZ12345")
        self.assertEqual(nowy_sprzet.name, "PC-IT-001")

    def test_read_asset_list(self):
        """Testuje, czy lista sprzętu ładuje się poprawnie (status 200) i wyświetla dodany sprzęt."""
        Asset.objects.create(
            serial_number="READ123",
            name="PC-READ-01",
            device_model=self.device_model,
            status="ACTIVE",
        )
        response = self.client.get(reverse("asset_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PC-READ-01")

    def test_update_asset(self):
        """Testuje edycję istniejącego sprzętu."""
        asset = Asset.objects.create(
            serial_number="OLD123",
            name="PC-OLD",
            device_model=self.device_model,
            status="IN_STOCK",
        )

        form_data = {
            "serial_number": "NEW123",
            "name": "PC-NEW",
            "device_model": self.device_model.id,
            "status": "ACTIVE",
        }
        response = self.client.post(
            reverse("asset_update", args=[asset.pk]), data=form_data
        )

        self.assertEqual(response.status_code, 302)

        asset.refresh_from_db()
        self.assertEqual(asset.name, "PC-NEW")
        self.assertEqual(asset.status, "ACTIVE")

    def test_delete_asset(self):
        """Testuje usuwanie sprzętu z bazy."""
        asset = Asset.objects.create(
            serial_number="DEL123", name="PC-TO-DELETE", device_model=self.device_model
        )

        self.assertEqual(Asset.objects.count(), 1)

        response = self.client.post(reverse("asset_delete", args=[asset.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Asset.objects.count(), 0)

    def test_create_asset_get(self):
        """Testuje, czy formularz tworzenia ładuje się poprawnie (GET)."""
        response = self.client.get(reverse("asset_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assets/asset_form.html")

    def test_update_asset_get(self):
        """Testuje, czy formularz edycji ładuje się poprawnie (GET)."""
        asset = Asset.objects.create(
            serial_number="UPD123", name="PC-UPD", device_model=self.device_model
        )
        response = self.client.get(reverse("asset_update", args=[asset.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assets/asset_form.html")

    def test_delete_asset_get(self):
        """Testuje, czy strona potwierdzenia usunięcia ładuje się poprawnie (GET)."""
        asset = Asset.objects.create(
            serial_number="DEL123", name="PC-DEL", device_model=self.device_model
        )
        response = self.client.get(reverse("asset_delete", args=[asset.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assets/asset_confirm_delete.html")

    def test_asset_list_search_and_invalid_sort(self):
        """Testuje gałęzie dla wyszukiwarki i nieprawidłowego sortowania."""
        Asset.objects.create(
            serial_number="SRC123", name="PC-SEARCH", device_model=self.device_model
        )

        # Test wyszukiwania (uruchomi linię if search_query)
        response_search = self.client.get(reverse("asset_list"), {"search": "SEARCH"})
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, "PC-SEARCH")

        # Test błędnego sortowania (uruchomi linię if sort_by not in valid_sorts)
        response_sort = self.client.get(
            reverse("asset_list"), {"sort": "zhakowane_sortowanie"}
        )
        self.assertEqual(response_sort.status_code, 200)

    def test_add_device_model_htmx_get(self):
        """Testuje ładowanie modala HTMX (GET)."""
        response = self.client.get(reverse("add_device_model_htmx"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assets/partials/device_model_form.html")

    def test_add_device_model_htmx_post(self):
        """Testuje poprawne zapisanie modelu przez HTMX (POST)."""
        form_data = {"manufacturer": "Lenovo", "name": "ThinkPad T14"}
        response = self.client.post(reverse("add_device_model_htmx"), data=form_data)

        self.assertEqual(response.status_code, 200)
        # Sprawdzamy czy widok zwraca nagłówek dla HTMX zamykający modal
        self.assertEqual(response["HX-Trigger"], "closeModal")
        # Sprawdzamy czy w zwróconym HTMLu jest nowy sprzęt
        self.assertContains(response, "Lenovo ThinkPad T14")

    def test_add_purchase_order_htmx_get(self):
        """Testuje ładowanie modala HTMX (GET)."""
        response = self.client.get(reverse("add_purchase_order_htmx"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "assets/partials/purchase_order_form.html")

    def test_add_purchase_order_htmx_post(self):
        """Testuje poprawne zapisanie modelu przez HTMX (POST)."""
        form_data = {
            "number": "PO-123",
            "supplier": "Amazon",
            "order_date": "2026-03-03",
        }
        response = self.client.post(reverse("add_purchase_order_htmx"), data=form_data)

        self.assertEqual(response.status_code, 200)
        # Sprawdzamy czy widok zwraca nagłówek dla HTMX zamykający modal
        self.assertEqual(response["HX-Trigger"], "closeModal")
        # Sprawdzamy czy w zwróconym HTMLu jest nowe zamówienie
        self.assertContains(response, "PO-123 Amazon")
