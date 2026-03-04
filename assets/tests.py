from django.test import TestCase
from django.urls import reverse
from .models import Asset, DeviceModel

# Create your tests here.

class AssetCRUDTests(TestCase):
    def setUp(self):
        self.device_model = DeviceModel.objects.create(
            manufacturer = "Dell",
            name = "Latitude 5520"
        )

    def test_create_asset_success(self):
        """Test czy jest poprawnie tworzony nowy sprzet"""
        self.assertEqual(Asset.objects.count(), 0)

        form_data = {
            'serial_number': 'XYZ12345',
            'name': 'PC-IT-001',
            'device_model': self.device_model.id,
            'status': 'ACTIVE',
        }

        response = self.client.post(reverse('asset_create'), data=form_data)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Asset.objects.count(), 1)

        nowy_sprzet = Asset.objects.first()
        self.assertEqual(nowy_sprzet.serial_number, 'XYZ12345')
        self.assertEqual(nowy_sprzet.name, 'PC-IT-001')

    def test_read_asset_list(self):
        """Testuje, czy lista sprzętu ładuje się poprawnie (status 200) i wyświetla dodany sprzęt."""
        Asset.objects.create(
            serial_number='READ123',
            name='PC-READ-01',
            device_model=self.device_model,
            status='ACTIVE'
        )
        response = self.client.get(reverse('asset_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PC-READ-01')

    def test_update_asset(self):
        """Testuje edycję istniejącego sprzętu."""
        asset = Asset.objects.create(
            serial_number='OLD123',
            name='PC-OLD',
            device_model=self.device_model,
            status='IN_STOCK'
        )
        
        form_data = {
            'serial_number': 'NEW123',
            'name': 'PC-NEW',
            'device_model': self.device_model.id,
            'status': 'ACTIVE'
        }
        response = self.client.post(reverse('asset_update', args=[asset.pk]), data=form_data)
        
        self.assertEqual(response.status_code, 302)
        
        asset.refresh_from_db()
        self.assertEqual(asset.name, 'PC-NEW')
        self.assertEqual(asset.status, 'ACTIVE')

    def test_delete_asset(self):
        """Testuje usuwanie sprzętu z bazy."""
        asset = Asset.objects.create(
            serial_number='DEL123',
            name='PC-TO-DELETE',
            device_model=self.device_model
        )
        
        self.assertEqual(Asset.objects.count(), 1)
        
        response = self.client.post(reverse('asset_delete', args=[asset.pk]))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Asset.objects.count(), 0)