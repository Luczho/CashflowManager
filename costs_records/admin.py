from django.contrib import admin
from .models import Cost, Company, Invoice, ExchangeRate, BankAccount, Address

admin.site.register(Cost)
admin.site.register(Company)
admin.site.register(Invoice)
admin.site.register(ExchangeRate)
admin.site.register(BankAccount)
admin.site.register(Address)

# Register your models here.
