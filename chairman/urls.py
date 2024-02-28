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
from chairman import views

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('login_check/', views.login_check, name='login_check'),
    path('add_member/', views.add_member, name='add_member'),
    path('store_member/', views.store_member, name='store_member'),
    path('view_member/', views.view_member, name='view_member'),
    path('member_details/<int:id>', views.member_details, name='member_details'),
    path('remove_member/<int:id>', views.remove_member, name='remove_member'),
    path('edit_member/<int:id>', views.edit_member, name='edit_member'),
    # path('update_member/<int:id>', views.update_member, name='update_member'),

    path('add_event/', views.add_event, name='add_event'),
    path('store_event/', views.store_event, name='store_event'),
    path('all_events/', views.all_events, name='all_events'),
    path('remove_event/<int:id>', views.remove_event, name='remove_event'),
    path('edit_event/<int:id>', views.edit_event, name='edit_event'),
    path('update_event/<int:id>', views.update_event, name='update_event'),

    path('schedule_meeting/', views.schedule_meeting, name='schedule_meeting'),
    path('store_meeting/', views.store_meeting, name='store_meeting'),
    path('all_meeting/', views.all_meeting, name='all_meeting'),
    path('remove_meeting/<int:id>', views.remove_meeting, name='remove_meeting'),
    path('edit_meeting/<int:id>', views.edit_meeting, name='edit_meeting'),
    path('update_meeting/<int:id>', views.update_meeting, name='update_meeting'),

    path('add_maintenance/', views.add_maintenance, name='add_maintenance'),
    path('store_maintenance/', views.store_maintenance, name='store_maintenance'),
    path('all_maintenance/', views.all_maintenance, name='all_maintenance'),
    path('remove_maintenance/<int:id>', views.remove_maintenance, name='remove_maintenance'),
    path('edit_maintenance/<int:id>', views.edit_maintenance, name='edit_maintenance'),
    path('update_maintenance/<int:id>', views.update_maintenance, name='update_maintenance'),
    path('paid_maintenance/', views.paid_maintenance, name='paid_maintenance'),
    path('paid_maintenance_details/<int:id>', views.paid_maintenance_details, name='paid_maintenance_details'),
    path('search_maintenance/', views.search_maintenance, name='search_maintenance'),
    path('status_maintenance/', views.status_maintenance, name='status_maintenance'),
    # path('paid_due_maintenance/', views.paid_due_maintenance, name='paid_due_maintenance'),

    path('all_complaints/', views.all_complaints, name='all_complaints'),
    path('complaint_details/<int:id>', views.complaint_details, name='complaint_details'),
    path('remove_complaint/<int:id>', views.remove_complaint, name='remove_complaint'),


    path('customer_report/', views.customer_report, name='customer_report'),
    path('pdf/', views.GeneratePdf.as_view()),

    path('maintenance_report/', views.maintenance_report, name='maintenance_report'),
    path('pdf2/', views.GeneratePdf2.as_view()),

    path('event_report/', views.event_report, name='event_report'),
    path('pdf3/', views.GeneratePdf3.as_view()),
]
