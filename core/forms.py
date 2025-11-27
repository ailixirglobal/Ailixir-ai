from django import forms
from .models import AISetting

class AISettingForm(forms.ModelForm):
    class Meta:
        model = AISetting
        fields = '__all__'