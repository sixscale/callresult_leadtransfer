from django.urls import path

from .views import LeadTransferAPIView, LeadCreationAPIView

urlpatterns = [
    path('lead-moloko/', LeadCreationAPIView.as_view(), name='lead-moloko'),
    path('lead-transfer/', LeadTransferAPIView.as_view(), name='lead_transfer'),
]
