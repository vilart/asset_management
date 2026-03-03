from django.shortcuts import render
from .models import Asset
# Create your views here.

def asset_list(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'name')

    valid_sorts = ['name', '-name', 'device_model__manufacturer', '-device_model__manufacturer', 'serial_number', '-serial_number', 'status', '-status']
    if sort_by not in valid_sorts:
        sort_by = 'name'

    if search_query:
        assets = Asset.objects.filter(name__icontains=search_query) | \
        Asset.objects.filter(serial_number__icontains=search_query) | \
        Asset.objects.filter(device_model__manufacturer__icontains=search_query)
    else:
        assets = Asset.objects.all()

    assets = assets.order_by(sort_by)

    context = {
        'assets': assets,
        'current_sort': sort_by
    }   
    return render(request, 'assets/asset_list.html', context)