from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


# BaseUserManager class contains create_user and create_superuser methods
# We are inheriting from that to override them
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("User must have an email"))
        if not password:
            raise ValueError(_("User must have a password"))
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        # To hash the password even from the admin panel
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("User must have an email"))
        if not password:
            raise ValueError(_("User must have a password"))
        email = self.normalize_email(email)

        user = self.create_user(email=email, password=password, **extra_fields)

        user.is_staff = True
        user.is_superuser = True
        user.role = User.Role.ADMIN
        user.save(using=self._db)
        return user
    
    



class User(AbstractUser):

    # first arguement is stored in database, second is its human readable form that will be displayed in dropdowns
    class Role(models.TextChoices):
        ADMIN = "ADMIN" , 'Admin'
        TEACHING_STAFF = "TEACHING_STAFF" , 'Teaching Staff'
        NON_TEACHING_LAB_STAFF = "NON_TEACHING_LAB_STAFF" , 'Non Teaching Lab Staff'
        NON_TEACHING_NON_LAB_STAFF = "NON_TEACHING_NON_LAB_STAFF" , 'Non Teaching Non Lab Staff'

    # first arguement is stored in database, second is its human readable form that will be displayed in dropdowns
    class Gender(models.TextChoices):
        MALE = "MALE", 'Male'
        FEMALE = "FEMALE", 'Female'

    # first arguement is stored in database, second is its human readable form that will be displayed in dropdowns
    class Department(models.TextChoices):
        COMPUTER = "COMPUTER", 'Computer'
        COMMERCE = "COMMERCE", 'Commerce'
        PHYSICS = "PHYSICS", 'Physics'


    # fields coming from parent class AbstractUSer that will be used as-it-is in our custom User model are :
    # password, groups, user_permissions, is_superuser, is_staff, is_active, last_login, date_joined

    # fields from parent class AbstractUser that we want to NOT be present in our custom User model are:
    username = None
    first_name = None
    last_name = None
    date_joined = None

    # adding these new fields to our custom User model:
    email = models.CharField(max_length=32, unique=True, db_index=True)   #db_index is for faster queries
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=50, choices=Role.choices)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    
    # other fields:
    emp_code = models.CharField(max_length=30, blank=True)
    dept = models.CharField(max_length=50, choices=Department.choices, blank=True)
    address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    mobile_number = models.CharField(max_length=50, blank=True)
    
    date_of_joining = models.DateField(blank=True, null=True)

    # user_id will be used for authentication
    USERNAME_FIELD = 'email'  

    # without these fields, a User object can't be created:
    REQUIRED_FIELDS = ['name']

    # for overriding default create_user and create_superuser method because we have extra arguements to be dealt with
    objects = CustomUserManager()  

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'users'  # This sets the table name to 'users'
        verbose_name_plural = "Users"