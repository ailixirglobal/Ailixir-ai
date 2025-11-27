from django.urls import path
from . import views
urlpatterns = [
  path('v1/', views.v1_api_endpoint)
  ]