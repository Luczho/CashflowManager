import requests
from costs_records.models import ExchangeRate


def get_exchange_rates(table, start_date=None, end_date=None):
    if start_date and end_date:
        url = f"http://api.nbp.pl/api/exchangerates/tables/{table}/{start_date}/{end_date}"
    else:
        url = f"http://api.nbp.pl/api/exchangerates/tables/{table}/"

    used_currencies = ['EUR', 'USD', 'CZK', 'HUF', 'RON', 'PLN']

    response = requests.get(url)

    for table in response.json():
        date = table['effectiveDate']
        for rate in table['rates']:
            if rate['code'] in used_currencies:
                currency = rate['code']
                rate = rate['mid']
                if not ExchangeRate.objects.filter(date=date, currency=currency).first():
                    ex_obj = ExchangeRate.objects.create(date=date, currency=currency, rate=rate)
                    ex_obj.save()


def run():
    get_exchange_rates("A", '2024-01-08', '2024-02-27')


