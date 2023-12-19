from django.db import models


class Company(models.Model):
    symbol = models.CharField(max_length=10, help_text='symbol of the company')
    name = models.CharField(max_length=100)
    vat_eu = models.CharField(max_length=20)
    is_contractor = models.BooleanField()


    def __str__(self):
        return self.name


class Address(models.Model):
    company = models.OneToOneField(Company, on_delete=models.DO_NOTHING)
    street_name = models.CharField(max_length=50)
    building_number = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=30)


class BankAccount(models.Model):
    EURO = "EUR"
    ZLOTY = "PLN"
    DOLAR = "USD"
    KORONA = "CZK"
    LEJ = "RON"
    FORINT = "HUF"
    CURRENCY_CHOICES = [
        (EURO, "Euro"),
        (ZLOTY, "Zloty"),
        (DOLAR, "Dolar"),
        (KORONA, "Korona"),
        (LEJ, "Lej"),
        (FORINT, "Forint")
    ]

    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    bank_name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=ZLOTY)
    country_code = models.CharField(max_length=20)
    account_number = models.CharField(max_length=30)


class ExchangeRate(models.Model):
    date = models.DateField(auto_now_add=True)
    currency = models.CharField(max_length=5)


class Invoice(models.Model):
    EURO = "EUR"
    ZLOTY = "PLN"
    DOLAR = "USD"
    KORONA = "CZK"
    CURRENCY_CHOICES = [
        (EURO, "Euro"),
        (ZLOTY, "Zloty"),
        (DOLAR, "Dolar"),
        (KORONA, "Korona")
    ]

    date = models.DateField()
    number = models.CharField(max_length=50)
    proforma = models.BooleanField(default=False)
    due_date = models.DateField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=ZLOTY)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pln_gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pln_net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.IntegerField()
    file = models.FileField(null=True)
    printed = models.BooleanField(default=False)
    in_optima = models.BooleanField(default=False)


class Cost(models.Model):
    uid = models.CharField(max_length=50, help_text='unique id of the cost id_created_date_company_symbol ex. 1_2020-01-01_NUT')
    created_date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='customer_costs') # company.costs.all()
    supplier = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='supplier_costs')
    cost_description = models.TextField()
    invoice = models.OneToOneField(Invoice, blank=True, null=True, on_delete=models.DO_NOTHING)
    paid = models.BooleanField(default=False)
    payment_date = models.DateField()
    asap = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.uid = f"{self.id}_{self.created_date}_{self.customer.symbol}"
        if self.payment_date:
            self.paid = True
        super().save(force_insert, force_update, using, update_fields)


