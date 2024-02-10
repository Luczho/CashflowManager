import datetime
from datetime import timedelta
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, TemplateView, FormView, DetailView, UpdateView, View
from django_filters.views import FilterView
from .models import Cost, Company, Address, Invoice, ExchangeRate
from .forms import CostForm, InvoiceForm, CompanyForm, AddressForm
from .filters import CostFilter
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator


def about(request):
    return render(request, 'costs_records/settings.html', {'title': 'About'})


class CostListView(ListView):
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


class AsapCostListView(ListView):
    model = Cost
    template_name = 'costs_records/costs-table-asap.html'
    context_object_name = 'costs'


class UrgentCostListView(ListView):
    model = Cost
    template_name = 'costs_records/costs-table-urgent.html'
    context_object_name = 'costs'


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
                date_string = current_date.strftime('%Y-%m-%d')
                ex_rate = ExchangeRate.objects.get(date=date_string, currency=invoice.currency)
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

        return invoice


class AddCostView(TemplateView, InvoiceMixin):

    template_name = 'costs_records/add-cost-form.html'

    def post(self, request, *args, **kwargs):

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_form'] = CostForm(prefix='cost')
        context['invoice_form'] = InvoiceForm(prefix='invoice')

        return context


class UpdateCostView(InvoiceMixin, UpdateView):

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

        return redirect('costs-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_form'] = CostForm(prefix='cost', initial=self.get_initial())
        context['invoice_form'] = InvoiceForm(prefix='invoice', initial=self.get_initial())

        return context

    def get_initial(self):
        initial = super(UpdateCostView, self).get_initial()
        cost_object = self.object
        invoice_object = cost_object.invoice
        # to refactor like update in invoice_object
        initial.update({'customer': cost_object.customer, 'cost_description': cost_object.cost_description,
                       'supplier': cost_object.supplier, 'estimated_cost': cost_object.estimated_cost,
                        'payment_date': cost_object.payment_date, 'asap': cost_object.asap, 'urgent': cost_object.urgent})
        if invoice_object:
            fields = ['date', 'number', 'proforma', 'due_date', 'currency', 'gross_amount', 'net_amount',
                      'pln_gross_amount', 'pln_net_amount', 'vat_rate', 'file', 'printed', 'in_optima']

            dct = {field: getattr(invoice_object, field) for field in fields if getattr(invoice_object, field)}
            initial.update(dct)
            # initial.update({'date': invoice_object.date,
            #                 'number': invoice_object.number, 'proforma': invoice_object.proforma,
            #                 'due_date': invoice_object.due_date, 'currency': invoice_object.currency,
            #                 'gross_amount': invoice_object.gross_amount, 'net_amount': invoice_object.net_amount,
            #                 'pln_gross_amount': invoice_object.pln_gross_amount,
            #                 'pln_net_amount': invoice_object.pln_net_amount, 'vat_rate': invoice_object.vat_rate,
            #                 'file': invoice_object.file, 'printed': invoice_object.printed,
            #                 'in_optima': invoice_object.in_optima})
        #
        return initial


class AsapUpdateCostView(View):
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



class AddCompanyView(TemplateView):

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
class CostDetailView(DetailView):
    model = Cost
    template_name = 'costs_records/cost-detail.html'


class CostFilterView(FilterView):

    filterset_class = CostFilter
    model = Cost

    template_name = 'costs_records/costs-table_filter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CostFilter(self.request.GET, queryset=self.get_queryset())
        context['cost_fields'] = Cost._meta.get_fields()
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

