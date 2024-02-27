from django.urls import path
from . import views
from .views import CostListView, AddCostView, AddCompanyView, CostDetailView, UpdateCostView, AsapCostListView,\
    InvoiceListView, AsapUpdateCostView, CostFilterView, PaymentUpdateCostView, CopyCostView

urlpatterns = [
    path('', views.about, name='cost-about'),
    path('costs/', CostListView.as_view(), name='costs-list'),
    path('costs/asap/', AsapCostListView.as_view(), name='costs-list-asap'),
    path('cost/add/', AddCostView.as_view(), name='add-cost'),
    path('cost/copy/<int:pk>/', CopyCostView.as_view(), name='copy-cost'),
    path('update/cost/<int:pk>/', UpdateCostView.as_view(), name='update-cost'),
    path('add/company/', AddCompanyView.as_view(), name='add-company'),
    path('cost/<int:pk>/', CostDetailView.as_view(), name='cost-detail'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('update/cost/asap/<int:pk>/', AsapUpdateCostView.as_view(), name='update-cost-asap'),
    path('update/cost/payment/<int:pk>/', PaymentUpdateCostView.as_view(), name='update-cost-payment'),
    path('costs/filter', CostFilterView.as_view(), name="costs-list-filter"),

]