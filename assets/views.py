from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Asset, DeviceModel
from .forms import AssetForm, DeviceModelForm
from django.views.decorators.http import require_GET, require_http_methods
# Create your views here.

@require_GET
def asset_list(request):
    search_query = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "name")

    valid_sorts = [
        "name",
        "-name",
        "device_model__manufacturer",
        "-device_model__manufacturer",
        "serial_number",
        "-serial_number",
        "status",
        "-status",
    ]
    if sort_by not in valid_sorts:
        sort_by = "name"

    if search_query:
        assets = (
            Asset.objects.filter(name__icontains=search_query)
            | Asset.objects.filter(serial_number__icontains=search_query)
            | Asset.objects.filter(device_model__manufacturer__icontains=search_query)
        )
    else:
        assets = Asset.objects.all()

    assets = assets.order_by(sort_by)

    context = {"assets": assets, "current_sort": sort_by}
    return render(request, "assets/asset_list.html", context)

@require_http_methods(["GET", "POST"])
def asset_create(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("asset_list")
    else:
        form = AssetForm()
    return render(request, "assets/asset_form.html", {"form": form})

@require_http_methods(["GET", "POST"])
def add_device_model_htmx(request):
    if request.method == "POST":
        form = DeviceModelForm(request.POST)
        if form.is_valid():
            new_model = form.save()

            models = DeviceModel.objects.all()

            html = '<option value ="">---------</option>'
            for m in models:
                selected = "selected" if m.id == new_model.id else ""
                html += f'<option value="{m.id}" {selected}>{m.manufacturer} {m.name}</option>'

            response = HttpResponse(html)
            response["HX-Trigger"] = "closeModal"
            return response
    else:
        form = DeviceModelForm()
    return render(request, "assets/partials/device_model_form.html", {"form": form})

@require_http_methods(["GET", "POST"])
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == "POST":
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect("asset_list")
    else:
        form = AssetForm(instance=asset)

    return render(request, "assets/asset_form.html", {"form": form, "asset": asset})

@require_http_methods(["GET", "POST"])
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == "POST":
        asset.delete()
        return redirect("asset_list")
    return render(request, "assets/asset_confirm_delete.html", {"asset": asset})
