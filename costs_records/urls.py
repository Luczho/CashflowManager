from django.urls import path
from . import views
from .views import CostListView

urlpatterns = [
    path('', views.about, name='cost-about'),
    path('costs/', CostListView.as_view(), name='costs-list')
]