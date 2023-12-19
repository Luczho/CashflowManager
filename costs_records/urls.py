from django.urls import path
from . import views
from .views import CostListView, AddCostView, AddCompanyView

urlpatterns = [
    path('', views.about, name='cost-about'),
    path('costs/', CostListView.as_view(), name='costs-list'),
    path('add/', AddCostView.as_view(), name='add-cost'),
    path('add/company/', AddCompanyView.as_view(), name='add-company')
]