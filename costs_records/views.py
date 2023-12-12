from django.shortcuts import render
from django.views.generic import ListView
from .models import Cost


def about(request):
    return render(request, 'costs_records/bootstrap-tables.html', {'title': 'About'})


class CostListView(ListView):
    model = Cost
    template_name = 'costs_records/costs-table.html'
    context_object_name = 'costs'

    fields_names = Cost._meta.get_fields()
