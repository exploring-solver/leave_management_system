from django import forms
from .models import LeaveApplications

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplications
        fields = ['leave_category', 'description', 'from_date', 'to_date']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
        }
