import django_filters
from django_filters.widgets import DateRangeWidget
from .models import Cost, Company
from django.forms.widgets import DateInput


class CostFilter(django_filters.FilterSet):
    created_date_range = django_filters.DateFromToRangeFilter(
        field_name='created_date', widget=DateRangeWidget(attrs={'type': 'date'}))
    due_date_range = django_filters.DateFromToRangeFilter(
        field_name='invoice__due_date', widget=DateRangeWidget(attrs={'type': 'date'}))
    due_date = django_filters.DateFromToRangeFilter(field_name='invoice__due_date')

    invoice_number = django_filters.CharFilter(field_name='invoice__number', lookup_expr='icontains')
    cost_description = django_filters.CharFilter(field_name='cost_description', lookup_expr='icontains')

    o = django_filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('created_date', 'created_date'),
            ('invoice__due_date', 'due_date'),
            ('invoice__days_to_due_date', 'days_to_due_date'))
    )

    class Meta:
        model = Cost
        fields = ['created_date_range', 'invoice_number', 'customer', 'supplier', 'cost_description',
                  'due_date_range', 'paid', 'invoice__currency']

    def __init__(self, *args, **kwargs):
        super(CostFilter, self).__init__(*args, **kwargs)

        self.filters['customer'].queryset = Company.objects.filter(is_contractor=False)
        self.filters['supplier'].queryset = Company.objects.filter(is_contractor=True)