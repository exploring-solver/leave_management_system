from django.db import models
from authentication.models import User


class LeaveCategories(models.Model):
    
    leave_type = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    class Meta:
        db_table = "leave_categories"
        verbose_name_plural = "Leave Categories"
        
    def __str__(self):
        return self.leave_type
        
        
class EmployeeLeaves(models.Model):
    
    emp_name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column = "user")
    
    leave_category = models.ForeignKey(LeaveCategories, on_delete=models.SET_NULL, null=True, db_column = "leaves_in_category1")
    leaves_remaining = models.IntegerField()

    
    
    
class LeaveApplications(models.Model):
    
    class Half(models.TextChoices):
        FIRST_HALF = "FIRST_HALF", 'First Half'
        SECOND_HALF = "SECOND_HALF", 'Second Half'
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column = "user", blank=True)
    
    leave_category = models.ForeignKey(LeaveCategories, on_delete=models.SET_NULL, null=True, db_column = "leave_category")    
    description = models.TextField(blank=True)
    
    applied_on = models.DateField(auto_now_add=True)
    from_date = models.DateField()
    to_date = models.DateField()
    
    approved = models.BooleanField(default=False)
    past = models.BooleanField(default=False)
    
    which_half = models.CharField(max_length=20, choices=Half.choices, blank=True, null=True)
    
    class Meta:
        db_table = "leave_applications"
        verbose_name_plural ="Leave Applications"