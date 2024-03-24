from django.contrib import admin
from . models import EmployeeLeaves, LeaveApplications, LeaveCategories
# Register your models here.

class EmployeeLeavesAdmin(admin.ModelAdmin):
    list_display = ['emp_name', 'user', 'leave_category', 'leaves_remaining']
    
class LeaveApplicationsAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_category', 'from_date', 'to_date']
    
class LeaveCategoriesAdmin(admin.ModelAdmin):
    list_display = ['leave_type', 'description']

admin.site.register(EmployeeLeaves, EmployeeLeavesAdmin)
admin.site.register(LeaveApplications, LeaveApplicationsAdmin)
admin.site.register(LeaveCategories, LeaveCategoriesAdmin)