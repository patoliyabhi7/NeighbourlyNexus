"""djtrain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from member import views

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('login_check/', views.login_check, name='login_check'),

    path('member_details/', views.member_details, name='member_details'),
    path('edit_profile/<int:id>', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('spasse/', views.spasse, name='spasse'),

    path('all_events/', views.all_events, name='all_events'),
    path('all_meeting/', views.all_meeting, name='all_meeting'),
    path('all_maintenance/', views.all_maintenance, name='all_maintenance'),

    path('complaint/', views.complaint, name='complaint'),
    path('post_complaint/', views.post_complaint, name='post_complaint'),
    path('all_complaints/', views.all_complaints, name='all_complaints'),
    path('remove_complaint/<int:id>', views.remove_complaint, name='remove_complaint'),
    path('edit_complaint/<int:id>', views.edit_complaint, name='edit_complaint'),
    path('update_complaint/<int:id>', views.update_complaint, name='update_complaint'),

    path('make_payment/<int:id>', views.make_payment, name='make_payment'),
    path('make_payment_event/<int:id>', views.make_payment_event, name='make_payment_event'),
    path('success/', views.success, name='success'),
    path('r_details/<int:id>', views.r_details, name='r_details'),
    path('r_details_event/<int:id>', views.r_details_event, name='r_details_event'),
    path('paid_maintenance/', views.paid_maintenance, name='paid_maintenance'),
    path('paid_event/', views.paid_event, name='paid_event'),



]
