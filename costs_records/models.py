from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Company(models.Model):
    symbol = models.CharField(max_length=10, help_text='Symbol of the company, ex. NUT, SPX')
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
        (EURO, "EUR"),
        (ZLOTY, "PLN"),
        (DOLAR, "USD"),
        (KORONA, "CZK"),
        (LEJ, "RON"),
        (FORINT, "HUF")
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
        (EURO, "EUR"),
        (ZLOTY, "PLN"),
        (DOLAR, "USD"),
        (KORONA, "CZK")
    ]

    PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

    date = models.DateField()
    number = models.CharField(max_length=50)
    proforma = models.BooleanField(default=False)
    due_date = models.DateField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pln_gross_amount = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    pln_net_amount = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=3, decimal_places=0, default=0, validators=PERCENTAGE_VALIDATOR)
    file = models.FileField(null=True, upload_to='invoices')
    printed = models.BooleanField(default=False)
    in_optima = models.BooleanField(default=False)

    def __str__(self):
        return self.number


class Cost(models.Model):
    CATEGORY_CHOICES = [
        ("OPERATION", "OPERATION"),
        ("MEDIA", "MEDIA"),
        ("PRODUCTION", "PRODUCTION")
    ]

    uid = models.CharField(max_length=50, help_text='unique id of the cost id_created_date_company_symbol ex. 1_2020-01-01_NUT')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='customer_costs')
    supplier = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='supplier_costs')
    cost_description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    invoice = models.OneToOneField(Invoice, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='cost')
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(blank=True, null=True)
    asap = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # self.uid = f"{self.id}_{self.created_date}_{self.customer.symbol}"
        if self.payment_date:
            self.paid = True
        super().save(force_insert, force_update, using, update_fields)


