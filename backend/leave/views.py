from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .decorators import admin_only
from .models import LeaveApplications, EmployeeLeaves, LeaveCategories
from .forms import LeaveApplicationForm
from django.contrib.auth import authenticate, login, logout
from authentication.models import User
from datetime import datetime, timedelta
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

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
    
    # Calculate total initial leaves allotted to the employee category-wise
    total_leaves = {}
    for category in employee_leaves:
        category_name = category.leave_category.leave_type

        if category_name not in total_leaves:
            total_leaves[category_name] = 0
        
        role = user.role
        gender = user.gender
        date_of_joining = user.date_of_joining

        if role == User.Role.TEACHING_STAFF:
            if gender == User.Gender.MALE:
                if datetime.now().date() - date_of_joining < timedelta(days=3650):
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 10
                    elif category_name in ['P-Leave', 'Medical Leave']:
                        total_leaves[category_name] += 8
                    elif category_name == 'Half Days':
                        total_leaves[category_name] += 10
                elif datetime.now().date() - date_of_joining < timedelta(days=7300):
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 15
                    elif category_name in ['P-Leave', 'Medical Leave']:
                        total_leaves[category_name] += 8
                    elif category_name == 'Half Days':
                        total_leaves[category_name] += 10
                else:
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 20
                    elif category_name in ['P-Leave', 'Medical Leave']:
                        total_leaves[category_name] += 8
                    elif category_name == 'Half Days':
                        total_leaves[category_name] += 10
            else:
                if category_name == 'Casual Leave':
                    total_leaves[category_name] += 20
                elif category_name in ['P-Leave', 'Medical Leave']:
                    total_leaves[category_name] += 8
                elif category_name == 'Half Days':
                    total_leaves[category_name] += 10
        elif role == User.Role.NON_TEACHING_LAB_STAFF:
            if gender == User.Gender.FEMALE:
                if category_name == 'Medical Leave':
                    total_leaves[category_name] += 10
                elif category_name == 'Casual Leave':
                    total_leaves[category_name] += 20
                elif category_name == 'Half Days':
                    total_leaves[category_name] += 10
                elif category_name == 'P-Leave':
                    total_leaves[category_name] += 8
            else:
                if datetime.now().date() - date_of_joining < timedelta(days=3650):
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 10
                elif datetime.now().date() - date_of_joining < timedelta(days=7300):
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 15
                else:
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 20
                if category_name == 'P-Leave':
                    total_leaves[category_name] += 8
                elif category_name == 'Half Days':
                    total_leaves[category_name] += 10
                elif category_name == 'Medical Leave':
                    total_leaves[category_name] += 10
        elif role == User.Role.NON_TEACHING_NON_LAB_STAFF:
            if gender == User.Gender.FEMALE:
                if category_name == 'Medical Leave':
                    total_leaves[category_name] += 10
                elif category_name == 'Casual Leave':
                    total_leaves[category_name] += 20
                elif category_name == 'Half Days':
                    total_leaves[category_name] += 10
                elif category_name == 'P-Leave':
                    total_leaves[category_name] += 0
            else:
                if datetime.now().date() - date_of_joining < timedelta(days=3650):
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 10
                elif datetime.now().date() - date_of_joining < timedelta(days=7300):
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 15
                else:
                    if category_name == 'Casual Leave':
                        total_leaves[category_name] += 20
                if category_name == 'P-Leave':
                    total_leaves[category_name] += 0
                elif category_name == 'Half Days':
                    total_leaves[category_name] += 10
                elif category_name == 'Medical Leave':
                    total_leaves[category_name] += 10
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            leave_application = form.save(commit=False)
            leave_application.user = user
            print(request.POST.get("attachment"))
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

            if form.cleaned_data['leave_category'].leave_type == 'Casual Leave' and applied_leaves > 2:
                messages.info(request, 'Number of Casual leaves applied can be only for 2 days.')
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

            # Subtract the applied leaves from the leaves remaining
            user_leave_category.leaves_remaining -= applied_leaves
            user_leave_category.save()
            
            # Subtract 0.5 from Casual Leave category if the leave category is Half Days
            if request.POST.get('which_half') != None :
                casual_leave_category = LeaveCategories.objects.get(leave_type='Casual Leave')
                casual_leave = EmployeeLeaves.objects.get(user=user, leave_category=casual_leave_category)
                casual_leave.leaves_remaining -= Decimal(0.5)
                casual_leave.save()

            # Save the leave application
            leave_application.save()
            messages.success(request, 'Leave Application Submitted Successfully')
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
        'employee_leaves': employee_leaves,
        'total_leaves': total_leaves
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
    
    # Additional context data
    total_registered_employees = User.objects.exclude(role=User.Role.ADMIN).count()
    listed_leave_types = LeaveCategories.objects.count()
    total_leaves = LeaveApplications.objects.count()
    approved_leaves = LeaveApplications.objects.filter(approved=True).count()
    new_leave_applications = LeaveApplications.objects.filter(past=False).count()
    
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
        'all_leave_categories': all_leave_categories,
        # Additional context data
        'total_registered_employees': total_registered_employees,
        'listed_leave_types': listed_leave_types,
        'total_leaves': total_leaves,
        'approved_leaves': approved_leaves,
        'new_leave_applications': new_leave_applications,
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
        emp_code = request.POST.get('emp_code')
        dept = request.POST.get('dept')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        mobile_number = request.POST.get('mobile_number')
        date_of_joining = datetime.strptime(request.POST.get('date_of_joining'), '%Y-%m-%d').date()

        # Create the user
        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
            role=role,
            gender=gender,
            emp_code=emp_code,
            dept=dept,
            address=address,
            city=city,
            country=country,
            mobile_number=mobile_number,
            date_of_joining=date_of_joining
        )
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







@login_required
def approve_leave(request, application_id):
    leave_application = LeaveApplications.objects.get(pk=application_id)
    leave_application.approved = True
    leave_application.past = True
    leave_application.admin_remark = request.POST.get('admin_remark', '')
    leave_application.save()
    messages.success(request, 'Leave Application Approved Successfully')
    return redirect('admin_dashboard')

@login_required
def disapprove_leave(request, application_id):
    leave_application = LeaveApplications.objects.get(pk=application_id)
    leave_application.approved = False
    leave_application.past = True
    leave_application.admin_remark = request.POST.get('admin_remark', '')
    leave_application.save()

    # Add the applied leaves back to the leaves remaining
    applied_leaves = (leave_application.to_date - leave_application.from_date).days + 1
    leave_category = leave_application.leave_category
    user_leave_category = EmployeeLeaves.objects.get(user=leave_application.user, leave_category=leave_category)
    user_leave_category.leaves_remaining += applied_leaves
    user_leave_category.save()

    # If the leave category is Half Days, add 0.5 leaves back to Casual Leave category
    if leave_application.which_half is not None:
        casual_leave_category = LeaveCategories.objects.get(leave_type='Casual Leave')
        casual_leave = EmployeeLeaves.objects.get(user=leave_application.user, leave_category=casual_leave_category)
        casual_leave.leaves_remaining += Decimal(0.5)
        casual_leave.save()

    messages.info(request, 'Leave Application Disapproved Successfully')
    return redirect('admin_dashboard')



@login_required
def toggle_user_status(request, user_id, action):
    user = User.objects.get(id=user_id)
    if action == 'active':
        user.is_active = True
        messages.success(request, f"{user.name} is now active.")
    elif action == 'inactive':
        user.is_active = False
        messages.success(request, f"{user.name} is now inactive.")
    user.save()
    return redirect('admin_dashboard')