from django.contrib import admin
from .models import Cost, Company, Invoice, ExchangeRate, BankAccount, Address

admin.site.register(Cost)
admin.site.register(Company)
admin.site.register(Invoice)
admin.site.register(BankAccount)
admin.site.register(Address)


class AdminExchangeRate(admin.ModelAdmin):
    list_display = ['pk', 'date', 'currency', 'rate']


admin.site.register(ExchangeRate, AdminExchangeRate)