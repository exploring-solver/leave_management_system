from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .decorators import admin_only
from .models import LeaveApplications, EmployeeLeaves, LeaveCategories
from .forms import LeaveApplicationForm
from django.contrib.auth import authenticate, login, logout
from authentication.models import User
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils import timezone

def home_page(request):
    return render(request, 'home.html')



@login_required
def dashboard(request):
    user = request.user

    # Fetch all leave categories for the user
    leave_categories = EmployeeLeaves.objects.filter(user=user)

    # Fetch all leaves for the user
    past_leaves = LeaveApplications.objects.filter(user=user, past=True)
    future_leaves = LeaveApplications.objects.filter(user=user, past=False)
    approved_leaves = LeaveApplications.objects.filter(user=user, approved=True)
    disapproved_leaves = LeaveApplications.objects.filter(user=user, approved=False, past=True)

    # Fetch employee leaves for the logged in user
    employee_leaves = EmployeeLeaves.objects.filter(user=user)

    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave_application = form.save(commit=False)
            leave_application.user = user

            # Calculate applied leaves
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            applied_leaves = (to_date - from_date).days + 1

            # Check if applied leaves exceed the leaves remaining
            leave_category_id = form.cleaned_data['leave_category'].id
            leave_category = LeaveCategories.objects.get(pk=leave_category_id)
            user_leave_category = EmployeeLeaves.objects.get(user=user, leave_category=leave_category)

            if from_date < timezone.now().date():
                messages.info(request, 'You cannot apply leave for dates in the past.')
                return redirect('dashboard')

            if form.cleaned_data['leave_category'].leave_type == 'Half Days' and from_date != to_date:
                messages.info(request, 'Both dates should be the same for half-day leaves')
                return redirect('dashboard')

            if from_date > to_date:
                messages.info(request, 'Please Select Valid Dates')
                return redirect('dashboard')

            if applied_leaves > user_leave_category.leaves_remaining:
                messages.info(request, 'You do not have enough leaves left for this category.')
                return redirect('dashboard')

            if applied_leaves == user_leave_category.leaves_remaining:
                leave_application.save()
                messages.info(request, 'Your leave has been exhausted contact the administrator')
                return redirect('dashboard')

            # Save the half-day option if applicable
            if request.POST.get('which_half') != '' :
                leave_application.which_half = request.POST.get('which_half')


            # Save the leave application
            leave_application.save()
            messages.info(request, 'Your leave have been Submitted Successfully')
            return redirect('dashboard')  # Redirect to dashboard after applying for leave
    else:
        form = LeaveApplicationForm()

    return render(request, 'dashboard.html', {
        'user': user,
        'form': form,
        'leave_categories': leave_categories,
        'past_leaves': past_leaves,
        'future_leaves': future_leaves,
        'approved_leaves': approved_leaves,
        'disapproved_leaves': disapproved_leaves,
        'employee_leaves': employee_leaves  # Add employee leaves to the context
    })

    
    
@login_required
def apply_for_leave(request):
    user = request.user
    employee_leaves = EmployeeLeaves.objects.filter(user=user).first()
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave_application = form.save(commit=False)
            leave_application.user = request.user
            leave_application.save()
            return redirect('dashboard')
        else:
            return HttpResponse(form.errors)
    else:
        form = LeaveApplicationForm()
        return redirect ('dashboard')
    
    # context = {
    #     'form': form,
    #     'employee_leaves': employee_leaves,
    # }
    # return render(request, 'dashboard.html', context)

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == User.Role.ADMIN:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            return HttpResponse('Invalid Credentials')
    return render(request, 'home.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def admin_dashboard(request):
    if request.user.role != User.Role.ADMIN:
        return HttpResponse("You are not authorized to access this page.")
    
    all_users = User.objects.all()
    all_leave_applications_pending = LeaveApplications.objects.filter(past=False, approved=False)
    all_leave_applications_approved = LeaveApplications.objects.filter(past=True, approved=True)
    all_leave_applications_disapproved = LeaveApplications.objects.filter(past=True, approved=False)
    all_employee_leaves = EmployeeLeaves.objects.all()
    all_leave_categories = LeaveCategories.objects.all()
    
    return render(request, 'admin_dashboard.html', {
        'all_users': all_users,
        'all_leave_applications_pending': all_leave_applications_pending,
        'all_leave_applications_approved': all_leave_applications_approved,
        'all_leave_applications_disapproved': all_leave_applications_disapproved,
        'all_employee_leaves': all_employee_leaves,
        'all_leave_categories': all_leave_categories
    })

    
    


from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import User, LeaveCategories, EmployeeLeaves

@login_required
def create_user(request):
    
    if request.method == 'POST':
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        gender = request.POST.get('gender')
        date_of_joining = datetime.strptime(request.POST.get('date_of_joining'), '%Y-%m-%d').date()

        # Create the user
        user = User.objects.create_user(email=email, password=password, name=name, role=role, gender=gender, date_of_joining=request.POST.get('date_of_joining'))

        # Determine leave categories dynamically based on role and date of joining
        leave_categories = ['Casual Leave', 'P-Leave', 'Medical Leave', 'Half Days']
        for category_name in leave_categories:
            category, _ = LeaveCategories.objects.get_or_create(leave_type=category_name)

            leaves_remaining = 0
            
            # Teaching Staff
            if role == User.Role.TEACHING_STAFF:
                # Male Teaching Staff
                if gender == User.Gender.MALE:
                    if datetime.now().date() - date_of_joining < timedelta(days=3650):
                        if category_name == 'Casual Leave':
                            leaves_remaining = 10
                        elif category_name in ['P-Leave', 'Medical Leave']:
                            leaves_remaining = 8
                        elif category_name == 'Half Days':
                            leaves_remaining = 10
                    elif datetime.now().date() - date_of_joining < timedelta(days=7300):
                        if category_name == 'Casual Leave':
                            leaves_remaining = 15
                        elif category_name in ['P-Leave', 'Medical Leave']:
                            leaves_remaining = 8
                        elif category_name == 'Half Days':
                            leaves_remaining = 10
                    else:
                        if category_name == 'Casual Leave':
                            leaves_remaining = 20
                        elif category_name in ['P-Leave', 'Medical Leave']:
                            leaves_remaining = 8
                        elif category_name == 'Half Days':
                            leaves_remaining = 10
                 # Female Teaching Staff
                else: 
                    if category_name == 'Casual Leave':
                        leaves_remaining = 20
                    elif category_name in ['P-Leave', 'Medical Leave']:
                        leaves_remaining = 8
                    elif category_name == 'Half Days':
                        leaves_remaining = 10
                        
            # Non Teaching Lad Staff
            elif role == User.Role.NON_TEACHING_LAB_STAFF:
                if gender == User.Gender.FEMALE:
                    if category_name == 'Medical Leave':
                        leaves_remaining = 10
                    elif category_name == 'Casual Leave':
                        leaves_remaining = 20
                    elif category_name == 'Half Days':
                        leaves_remaining = 10
                    elif category_name == 'P-Leave':
                        leaves_remaining = 8
                else:  # Male Non Teaching Lab Staff
                    if datetime.now().date() - date_of_joining < timedelta(days=3650):
                        if category_name == 'Casual Leave':
                            leaves_remaining = 10
                    elif datetime.now().date() - date_of_joining < timedelta(days=7300):
                        if category_name == 'Casual Leave':
                            leaves_remaining = 15
                    else:
                        if category_name == 'Casual Leave':
                            leaves_remaining = 20
                    if category_name == 'P-Leave':
                        leaves_remaining = 8
                    elif category_name == 'Half Days':
                        leaves_remaining = 10
                    elif category_name == 'Medical Leave':
                        leaves_remaining = 10
                        
            # Non Teaching NON Lab Staff
            elif role == User.Role.NON_TEACHING_NON_LAB_STAFF:
                if gender == User.Gender.FEMALE:
                    if category_name == 'Medical Leave':
                        leaves_remaining = 10
                    elif category_name == 'Casual Leave':
                        leaves_remaining = 20
                    elif category_name == 'Half Days':
                        leaves_remaining = 10
                    elif category_name == 'P-Leave':
                        leaves_remaining = 0
                else:  # Male Non Teaching Lab Staff
                    if datetime.now().date() - date_of_joining < timedelta(days=3650):
                        if category_name == 'Casual Leave':
                            leaves_remaining = 10
                    elif datetime.now().date() - date_of_joining < timedelta(days=7300):
                        if category_name == 'Casual Leave':
                            leaves_remaining = 15
                    else:
                        if category_name == 'Casual Leave':
                            leaves_remaining = 20
                    if category_name == 'P-Leave':
                        leaves_remaining = 0
                    elif category_name == 'Half Days':
                        leaves_remaining = 10
                    elif category_name == 'Medical Leave':
                        leaves_remaining = 10

            # Create employee leaves record
            EmployeeLeaves.objects.create(emp_name=user.name, user=user, leave_category=category, leaves_remaining=leaves_remaining)

        return redirect('admin_dashboard')

    return HttpResponse("Method not allowed.")
