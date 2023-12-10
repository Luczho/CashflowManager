from django.db import models


class Address(models.Model):
    street_name = models.CharField(max_length=50)
    building_number = models.CharField(max_length=20)
    postal_code = models.IntegerField()
    city = models.CharField(max_length=30)


class Company(models.Model):
    symbol = models.CharField(max_length=10, help_text='symbol of the company')
    name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='company') # address.object.first().company
    vat_eu = models.CharField(max_length=20)
    is_contractor = models.BooleanField()


class BankAccount(models.Model):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    bank_name = models.CharField(max_length=50)
    currency = models.CharField(max_length=20) # convert to choice field
    country_code = models.CharField(max_length=20)
    account_number = models.CharField()


class Invoice(models.Model):
    date = models.DateField()
    number = models.CharField(max_length=50)
    is_proforma = models.BooleanField(default=False)
    due_date = models.DateField()
    currency = models.CharField(max_length=20)
    gross_amount = models.DecimalField(max_digits=10)
    net_amount = models.DecimalField(max_digits=10)
    pln_net_amount = ...
    pln_gross_amount = ...


    # @property
    # def pln_amount(self):
    #     return self.gross_amount * ...
    #     ... # calculate net amount from gross amount and vat rate


# x = Invoice.objects.first().pln_amount

# class Item(models.Model):
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')

class ExchangeRate(models.Model):
    date = models.DateField(auto_now_add=True)
    currency = models.CharField


class Cost(models.Model):
    uid = models.CharField(max_length=50, help_text='unique id of the cost id_created_date_company_symbol ex. 1_2020-01-01_NUT')
    created_date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='costs') # cost.customer, customer.costs
    supplier = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='costs')
    cost_description = models.TextField()
    invoice = models.ForeignKey(Invoice, null=True, on_delete=models.DO_NOTHING, related_name='costs')
