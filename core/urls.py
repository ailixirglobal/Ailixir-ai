from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.edit_settings, name='edit_settings'),
    path('quick_prompts/<id>/', views.quick_prompt_interface, name='quick_prompt_interface'),
    path('', views.public_ai_interface, name='public_ai_interface'),
]