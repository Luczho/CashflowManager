from costs_records.models import Invoice
import datetime


def calculate_day_to_due_date():
    queryset = Invoice.objects.all()
    current_date = datetime.date.today()

    for obj in queryset:
        delta = current_date - obj.due_date
        obj.days_to_due_date = delta.days
        obj.save()


def run():
    calculate_day_to_due_date()
