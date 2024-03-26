from django.urls import path
from . import views

urlpatterns = [
    # path('categories/', views.leave_categories, name='leave_categories'),
    path('leave-apply/', views.apply_for_leave, name='apply_for_leave'),
    path('', views.home_page, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout ,name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-user/', views.create_user, name='create_user'),
    path('approve-leave/<int:application_id>/', views.approve_leave, name='approve_leave'),
    path('disapprove-leave/<int:application_id>/', views.disapprove_leave, name='disapprove_leave'),
    path('toggle-user-status/<int:user_id>/<str:action>/', views.toggle_user_status, name='toggle_user_status'),
]
