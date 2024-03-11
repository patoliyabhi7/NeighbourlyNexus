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
from myadmin import views

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('login_check/', views.login_check, name='login_check'),
    path('logout/', views.logout, name='logout'),

    path('add_chairman/', views.add_chairman, name='add_chairman'),
    path('store_chairman/', views.store_chairman, name='store_chairman'),
    path('view_chairman/', views.view_chairman, name='view_chairman'),
    path('remove_chairman/<int:id>', views.remove_chairman, name='remove_chairman'),

    path('view_member/', views.view_member, name='view_member'),
    path('member_details/<int:id>', views.member_details, name='member_details'),
    path('remove_member/<int:id>', views.remove_member, name='remove_member'),

    path('all_complaints/', views.all_complaints, name='all_complaints'),
    path('all_events/', views.all_events, name='all_events'),
    path('all_maintenance/', views.all_maintenance, name='all_maintenance'),
    path('all_meeting/', views.all_meeting, name='all_meeting'),
    path('complaint_details/<int:id>', views.complaint_details, name='complaint_details'),
    path('paid_maintenance/', views.paid_maintenance, name='paid_maintenance'),
    path('paid_maintenance_details/<int:id>', views.paid_maintenance_details, name='paid_maintenance_details'),
    path('edit_chairman/<int:id>', views.edit_chairman, name='edit_chairman'),
    path('update_chairman/<int:id>', views.update_chairman, name='update_chairman'),
    path('remove_event/<int:id>', views.remove_event, name='remove_event'),
    path('remove_meeting/<int:id>', views.remove_meeting, name='remove_meeting'),


    path('customer_report/', views.customer_report, name='customer_report'),
    path('pdf/', views.GeneratePdf.as_view()),

    path('maintenance_report/', views.maintenance_report, name='maintenance_report'),
    path('pdf2/', views.GeneratePdf2.as_view()),

    path('event_report/', views.event_report, name='event_report'),
    path('pdf3/', views.GeneratePdf3.as_view()),

]
