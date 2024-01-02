from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, TemplateView, FormView, DetailView
from .models import Cost, Company, Address
from .forms import CostForm, InvoiceForm, CompanyForm, AddressForm
from django.urls import reverse_lazy


def about(request):
    return render(request, 'costs_records/settings.html', {'title': 'About'})


class CostListView(ListView):
    model = Cost
    template_name = 'costs_records/costs-table.html'
    context_object_name = 'costs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_fields'] = Cost._meta.get_fields()
        return context


class AddCostView(TemplateView):

    template_name = 'costs_records/add-cost-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_form'] = CostForm(prefix='cost')
        context['invoice_form'] = InvoiceForm(prefix='invoice')

        return context

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

    def post(self, request, *args, **kwargs):
        invoice_form = InvoiceForm(self.request.POST, self.request.FILES, prefix='invoice')
        cost_form = CostForm(self.request.POST, self.request.FILES, prefix='cost')
        if all([cost_form.is_valid(), invoice_form.is_valid()]):
            cost = cost_form.save()
            cost.uid = f"{cost.id}_{cost.created_date}_{cost.customer.symbol}"
            if not self.check_if_invoice_form_is_empty(invoice_form):
                invoice = invoice_form.save()
                # cost = cost_form.save(commit=False)
                cost.invoice = invoice
                # cost.uid = f"{cost.id}_{cost.created_date}_{cost.customer.symbol}"
                cost.save()
            else:
                # cost = cost_form.save()
                # cost.uid = f"{cost.id}_{cost.created_date}_{cost.customer.symbol}"
                cost.save()


            return redirect('costs-list')

        # return super().post(request, *args, **kwargs)


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


class CostDetailView(DetailView):
    model = Cost
    template_name = 'costs_records/cost-detail.html'

