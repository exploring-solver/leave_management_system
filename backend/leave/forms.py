from django import forms
from .models import LeaveApplications, LeaveCategories, EmployeeLeaves
from authentication.models import Department

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplications
        fields = ['leave_category', 'description', 'from_date', 'to_date','attachment']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department']
        
class LeaveCategoryForm(forms.ModelForm):
    class Meta:
        model = LeaveCategories
        fields = ['leave_type', 'default_leaves']
        
class EmployeeLeavesForm(forms.ModelForm):
    class Meta:
        model = EmployeeLeaves
        fields = ['leaves_remaining']
        widgets = {
            'leaves_remaining': forms.NumberInput(attrs={'class': 'border-gray-300 border w-full px-3 py-2 rounded'})
        }