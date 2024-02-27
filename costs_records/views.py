import datetime
from datetime import timedelta
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, TemplateView, FormView, DetailView, UpdateView, View
from django_filters.views import FilterView
from .models import Cost, Company, Address, Invoice, ExchangeRate
from .forms import CostForm, InvoiceForm, CompanyForm, AddressForm, PaymentDateForm
from .filters import CostFilter
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


def about(request):
    return render(request, 'costs_records/settings.html', {'title': 'About'})


class CostListView(LoginRequiredMixin, ListView):
    model = Cost
    template_name = 'costs_records/costs-table.html'
    context_object_name = 'costs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_fields'] = Cost._meta.get_fields()
        context['total_ga'], context['total_na'], context['total_pga'], context['total_pna'], context['total_est']\
            = self.total_amounts()
        return context

    def total_amounts(self):

        invoices = Invoice.objects.filter(cost__isnull=False)
        costs = Cost.objects.all()
        total_ga = 0
        total_na = 0
        total_pga = 0
        total_pna = 0
        total_est = 0
        for invoice in invoices:
            total_ga += invoice.gross_amount
            total_na += invoice.net_amount
            if invoice.pln_net_amount and invoice.pln_net_amount:
                total_pga += invoice.pln_gross_amount
                total_pna += invoice.pln_net_amount
        for cost in costs:
            if cost.estimated_cost:
                total_est += cost.estimated_cost
        return total_ga, total_na, total_pga, total_pna, total_est


class AsapCostListView(LoginRequiredMixin, FilterView):
    model = Cost
    template_name = 'costs_records/costs-table-asap.html'
    context_object_name = 'costs'
    filterset_class = CostFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CostFilter(self.request.GET, queryset=self.get_queryset())
        context['pd_form'] = PaymentDateForm(prefix='pd')

        return context


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'costs_records/invoices-table.html'
    context_object_name = 'invoices'


class InvoiceMixin:
    def check_if_invoice_form_is_empty(self, invoice_form) -> bool:
        none_fields = ('date', 'due_date', 'gross_amount', 'net_amount')
        empty_string = ('currency', 'number')
        for field in invoice_form.cleaned_data:
            if field in none_fields:
                if invoice_form.cleaned_data[field] is not None:
                    return False
            if field in empty_string:
                if invoice_form.cleaned_data[field] != '':
                    return False

        return True

    def get_exchange_rate(self, date, currency, days_back) -> ExchangeRate:
        for i in range(days_back):
            try:
                ex_rate = ExchangeRate.objects.get(date=date, currency=currency)
                return ex_rate

            except ExchangeRate.DoesNotExist:
                date -= timedelta(days=1)

        raise ExchangeRate.DoesNotExist(f"No exchange rate found for {currency} in the past {days_back} days.")

    def calculate_pln_amounts(self, invoice, date=None) -> Invoice:
        if invoice.currency != 'PLN':
            if not date:
                current_date = datetime.date.today()
                one_day_back = current_date - timedelta(days=1)
                date_string = one_day_back.strftime('%Y-%m-%d')
                ex_rate = ExchangeRate.objects.get(date=date_string, currency=invoice.currency)
                # Przenieść do oddzielnej func
                invoice.pln_net_amount = round(invoice.net_amount * ex_rate.rate, 2)
                invoice.pln_gross_amount = round(invoice.gross_amount * ex_rate.rate, 2)
                invoice.save()
            else:
                ex_rate = self.get_exchange_rate(date, invoice.currency, 7)
                invoice.pln_net_amount = round(invoice.net_amount * ex_rate.rate, 2)
                invoice.pln_gross_amount = round(invoice.gross_amount * ex_rate.rate, 2)
                invoice.save()
        else:
            invoice.pln_net_amount = invoice.net_amount
            invoice.pln_gross_amount = invoice.gross_amount
            invoice.save()

        return invoice

    def cost_get_initial(self, view):
        initial = super(view, self).get_initial()
        cost_object = self.object
        invoice_object = cost_object.invoice
        fields = ['customer', 'cost_description', 'supplier', 'estimated_cost', 'payment_date', 'asap', 'urgent']
        dct = {field: getattr(cost_object, field)for field in fields if getattr(cost_object, field)}
        initial.update(dct)
        if invoice_object:
            fields = ['date', 'number', 'proforma', 'due_date', 'currency', 'gross_amount', 'net_amount',
                      'pln_gross_amount', 'pln_net_amount', 'vat_rate', 'file', 'printed', 'in_optima']
            dct = {field: getattr(invoice_object, field) for field in fields if getattr(invoice_object, field)}
            initial.update(dct)
        return initial

    def add_cost_post(self):
        invoice_form = InvoiceForm(self.request.POST, self.request.FILES, prefix='invoice')
        cost_form = CostForm(self.request.POST, self.request.FILES, prefix='cost')
        if all([cost_form.is_valid(), invoice_form.is_valid()]):
            cost = cost_form.save()
            cost.uid = f"{cost.id}_{cost.created_date}_{cost.customer.symbol}"
            if not self.check_if_invoice_form_is_empty(invoice_form):
                invoice = invoice_form.save()
                self.calculate_pln_amounts(invoice)
                cost.invoice = invoice
                cost.save()
            else:
                cost.save()
        else:
            messages.error('Something went wrong. Please try again.')

        return redirect('costs-list-filter')


class AddCostView(LoginRequiredMixin, TemplateView, InvoiceMixin):

    template_name = 'costs_records/add-cost-form.html'

    def post(self, request, *args, **kwargs):
        return self.add_cost_post()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_form'] = CostForm(prefix='cost')
        context['invoice_form'] = InvoiceForm(prefix='invoice')

        return context

class CopyCostView(LoginRequiredMixin, InvoiceMixin, UpdateView):

    model = Cost
    template_name = 'costs_records/add-cost-form.html'
    fields = "__all__"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = Cost.objects.get(pk=pk)
        return obj

    def post(self, request, *args, **kwargs):
        return self.add_cost_post()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_form'] = CostForm(prefix='cost', initial=self.get_initial())
        context['invoice_form'] = InvoiceForm(prefix='invoice', initial=self.get_initial())

        return context

    def get_initial(self):
        return self.cost_get_initial(CopyCostView)

class UpdateCostView(LoginRequiredMixin, InvoiceMixin, UpdateView):

    model = Cost
    template_name = 'costs_records/add-cost-form.html'
    fields = "__all__"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = Cost.objects.get(pk=pk)
        return obj

    def post(self, request, *args, **kwargs):
        cost_object = self.get_object()
        invoice_object = cost_object.invoice
        invoice_form = InvoiceForm(self.request.POST, self.request.FILES, prefix='invoice')
        cost_form = CostForm(self.request.POST, self.request.FILES, prefix='cost')
        if all([cost_form.is_valid(), invoice_form.is_valid()]):
            for form_field in cost_form.cleaned_data.keys():
                cost_object.__setattr__(form_field, cost_form.cleaned_data[form_field])
            cost_object.uid = f"{cost_object.id}_{cost_object.created_date}_{cost_object.customer.symbol}"
            if not self.check_if_invoice_form_is_empty(invoice_form):
                if invoice_object:
                    for form_field in invoice_form.cleaned_data.keys():
                        invoice_object.__setattr__(form_field, invoice_form.cleaned_data[form_field])
                    self.calculate_pln_amounts(invoice_object, cost_object.created_date)
                    invoice_object.save()
                else:
                    invoice_object = invoice_form.save()
                    self.calculate_pln_amounts(invoice_object, cost_object.created_date)
                cost_object.invoice = invoice_object
                cost_object.save()
            else:
                cost_object.save()
        else:
            messages.error(request, "Something went wrong. Please try again.")

        return redirect('costs-list-filter')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_form'] = CostForm(prefix='cost', initial=self.get_initial())
        context['invoice_form'] = InvoiceForm(prefix='invoice', initial=self.get_initial())

        return context

    def get_initial(self):
        return self.cost_get_initial(UpdateCostView)


class AsapUpdateCostView(LoginRequiredMixin, View):
    # Raczej nie potrzebne w tym widoku
    model = Cost
    fields = ['asap']

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        obj = Cost.objects.get(pk=pk)
        return obj

    def post(self, request, *args, **kwargs):
        cost_object = self.get_object()
        cost_object.asap = True
        cost_object.save()
        return redirect('costs-list')


class PaymentUpdateCostView(LoginRequiredMixin, View):
    # Raczej nie potrzebne w tym widoku
    model = Cost
    fields = ['payment_date']

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        obj = Cost.objects.get(pk=pk)
        return obj

    def post(self, request, *args, **kwargs):
        pd_form = PaymentDateForm(self.request.POST, self.request.FILES, prefix='pd')
        cost_obj = self.get_object()
        if pd_form.is_valid():
            if pd_form.cleaned_data['payment_date']:
                payment_date = pd_form.cleaned_data['payment_date']
                cost_obj.payment_date = payment_date
                cost_obj.save()
                return redirect('costs-list-asap')
            elif pd_form.cleaned_data['planned_payment_date']:
                params = request.POST.get('params')
                planned_payment_date = pd_form.cleaned_data['planned_payment_date']
                cost_obj.planned_payment_date = planned_payment_date
                cost_obj.save()
                return HttpResponseRedirect(f"{reverse('costs-list-filter')}?{params}")


class AddCompanyView(LoginRequiredMixin, TemplateView):

    template_name = 'costs_records/add-company-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_form'] = CompanyForm(prefix='company')
        context['address_form'] = AddressForm(prefix='address')

        return context

    def post(self, request, *args, **kwargs):
        company_form = CompanyForm(self.request.POST, self.request.FILES, prefix='company')
        address_form = AddressForm(self.request.POST, self.request.FILES, prefix='address')
        if all([company_form.is_valid(), address_form.is_valid()]):
            company = company_form.save()
            address = address_form.save(commit=False)
            address.company = company
            address.save()
            return redirect('add-cost')

        # return super().post(request, *args, **kwargs)


@method_decorator(xframe_options_exempt, name='dispatch')
class CostDetailView(LoginRequiredMixin, DetailView):
    model = Cost
    template_name = 'costs_records/cost-detail.html'


class CostFilterView(LoginRequiredMixin, FilterView):

    filterset_class = CostFilter
    model = Cost

    template_name = 'costs_records/costs-table_filter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CostFilter(self.request.GET, queryset=self.get_queryset())
        context['cost_fields'] = Cost._meta.get_fields()
        context['pd_form'] = PaymentDateForm(prefix='pd')
        context['total_ga'], context['total_na'], context['total_pga'], context['total_pna'], context['total_est'] \
            = self.total_amounts()

        return context

    def total_amounts(self):

        invoices = Invoice.objects.filter(cost__isnull=False)
        costs = Cost.objects.all()
        total_ga = 0
        total_na = 0
        total_pga = 0
        total_pna = 0
        total_est = 0
        for invoice in invoices:
            total_ga += invoice.gross_amount
            total_na += invoice.net_amount
            if invoice.pln_net_amount and invoice.pln_net_amount:
                total_pga += invoice.pln_gross_amount
                total_pna += invoice.pln_net_amount
        for cost in costs:
            if cost.estimated_cost:
                total_est += cost.estimated_cost
        return total_ga, total_na, total_pga, total_pna, total_est

    def get_queryset(self):
        user = self.request.user
        user_permissions = list(user.user_permissions.values_list('codename', flat=True))
        group_permissions = list(user.groups.values_list('permissions__codename', flat=True))
        all_permissions = user_permissions + group_permissions
        all_categories = [choice[0] for choice in Cost.CATEGORY_CHOICES]
        user_permissions = [perm.replace('can_view_', '').upper() for perm in all_permissions if perm.startswith('can_view_')]
        # user_categories = [perm.replace('can_view_', '').upper() for perm in view_permissions]
        user_categories = [category for category in user_permissions if category in all_categories]

        return super().get_queryset().filter(Q(category__in=user_categories) | Q(category__isnull=True))


