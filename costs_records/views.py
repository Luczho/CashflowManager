from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, TemplateView, FormView
from .models import Cost, Company, Address
from .forms import CostForm, InvoiceForm, CompanyForm, AddressForm
from django.urls import reverse_lazy


def about(request):
    return render(request, 'costs_records/bootstrap-tables.html', {'title': 'About'})


class CostListView(ListView):
    model = Cost
    template_name = 'costs_records/costs-table.html'
    context_object_name = 'costs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cost_fields'] = Cost._meta.get_fields()
        return context


class AddCostView(TemplateView):
    model = Cost
    template_name = 'costs_records/add-cost-form.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['forms'] = [CostForm, InvoiceForm]
    #
    #     return context

    def get(self, request, *args, **kwargs):
        cost_form = CostForm(prefix='cost')
        invoice_form = InvoiceForm(prefix='invoice')
        return render(self.request, 'costs_records/add-cost-form.html',
                      {'cost_form': cost_form, 'invoice_form': invoice_form})

        # return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        cost_form = CostForm(self.request.POST, self.request.FILES, prefix='cost')
        invoice_form = InvoiceForm(self.request.POST, self.request.FILES, prefix='invoice')
        if all([cost_form.is_valid(), invoice_form.is_valid()]):
            form = cost_form.save()
            invoice = invoice_form.save(commit=False)
            invoice.form = form
            invoice.save()
            return redirect('costs-list')

        return super().post(request, *args, **kwargs)


class AddCompanyView(TemplateView):
    model = Company, Address
    template_name = 'costs_records/add-company-form.html'

    def get(self, request, *args, **kwargs):
        company_form = CompanyForm(prefix='company')
        address_form = AddressForm(prefix='address')
        return render(self.request, 'costs_records/add-company-form.html', {'company_form': company_form,
                                                                            'address_form': address_form})

        # return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        company_form = CompanyForm(self.request.POST, self.request.FILES, prefix='company')
        address_form = AddressForm(self.request.POST, self.request.FILES, prefix='address')
        if all([company_form.is_valid(), address_form.is_valid()]):
            form = company_form.save()
            address = address_form.save(commit=False)
            address.form = form
            address.save()
            return redirect('add-cost')

        return super().post(request, *args, **kwargs)
