from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Asset, DeviceModel
from .forms import AssetForm, DeviceModelForm
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

def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm()
    return render(request, 'assets/asset_form.html', {'form':form})

def add_device_model_htmx(request):
    if request.method == 'POST':
        form = DeviceModelForm(request.POST)
        if form.is_valid():
            new_model = form.save()

            models = DeviceModel.objects.all()

            html = '<option value ="">---------</option>'
            for m in models:
                selected = 'selected' if m.id == new_model.id else ''
                html += f'<option value="{m.id}" {selected}>{m.manufacturer} {m.name}</option>'
            
            response = HttpResponse(html)
            response['HX-Trigger'] = 'closeModal'
            return response
    else:

        form = DeviceModelForm()
    return render(request, 'assets/partials/device_model_form.html', {'form': form})

        