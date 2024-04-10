from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from myadmin.models import *
from chairman.models import *
from member.models import *
from django.contrib import auth
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import datetime, date
from django.views.generic import View
from django.template.loader import render_to_string
from .process import html_to_pdf 
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.utils.dateparse import parse_date

def login(request):
    context={}
    return render(request, 'myadmin/login.html', context)

def login_check(request):
    username = request.POST['username']
    password = request.POST['password']

    result = auth.authenticate(username=username, password=password)

    if result is None:
        messages.success(request, 'Invalid username or password')
        print('Invalid username or password')
        return redirect('/myadmin/login/')

    else: 
        if Member.objects.filter(user_id=result.id).exists():
            messages.error(request, 'Invalid User..Try Again')
            return redirect('/myadmin/dashboard/')
            # auth.login(request, result)
            # return redirect('/myadmin/dashboard/')

        elif Chairman.objects.filter(user_id=result.id).exists():
            messages.error(request, 'Invalid User..Try Again')
            return redirect('/myadmin/dashboard/')

        else:
            auth.login(request, result)
            return redirect('/myadmin/dashboard/')
            # messages.error(request, 'Invalid User..Try Again')
            # return redirect('/myadmin/dashboard/')

def logout(request):

    print(request.user.id)
    auth.logout(request)
    print(request.user.id)
    return redirect('/myadmin/login/')

@login_required(login_url='/myadmin/login/')
def dashboard(request):
    print(request.user.id)
    context={}
    return render(request, 'myadmin/dashboard.html', context)

@login_required(login_url='/myadmin/login/')
def add_chairman(request):
    context={}
    return render(request, 'myadmin/add_chairman.html', context)

# def store_chairman(request):
#     first_name = request.POST['first_name']
#     last_name = request.POST['last_name']
#     username = request.POST['username']
#     password = request.POST['password']
#     cpassword = request.POST['cpassword']
#     email = request.POST['email']

#     gender = request.POST['gender']
#     phone = request.POST['phone']

#     if password == cpassword:
#         user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)

#         Chairman.objects.create(gender=gender,phone=phone,reg_date=date.today(),user_id=user.id)
#         return redirect('/myadmin/dashboard/')

#     else:
#         print('Password and confirm password mismatched')
#         return redirect('/myadmin/add_chairman/')

def store_chairman(request):
    # Extract data from request
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    cpassword = request.POST.get('cpassword', '').strip()
    email = request.POST.get('email', '').strip()
    gender = request.POST.get('gender', '').strip()
    phone = request.POST.get('phone', '').strip()

    # Perform basic validations
    if not (first_name and last_name and username and password and cpassword and email and gender and phone):
        # Check if any field is empty
        print('All fields are required.')
        messages.success(request, 'All fields are required.')
        return redirect('/myadmin/add_chairman/')

    if password != cpassword:
        # Check if password and confirm password match
        print('Password and confirm password mismatched')
        messages.success(request, 'Password and confirm password mismatched')
        return redirect('/myadmin/add_chairman/')

    if User.objects.filter(username=username).exists():
        # Check if username already exists
        print('Username already exists')
        messages.success(request, 'Username already exists')
        return redirect('/myadmin/add_chairman/')

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        print('Invalid email address')
        messages.success(request, 'Invalid email address')
        return redirect('/myadmin/add_chairman/')

    # Validate phone number format
    if not re.match(r'^\+?1?\d{9,15}$', phone):
        print('Invalid phone number format')
        messages.success(request, 'Invalid phone number format')
        return redirect('/myadmin/add_chairman/')

    # Validate password strength
    # You can define your own criteria for password strength
    if len(password) < 8:
        print('Password should be at least 8 characters long')
        messages.success(request, 'Password should be at least 8 characters long')
        return redirect('/myadmin/add_chairman/')
    elif not any(char.isdigit() for char in password):
        print('Password should contain at least one digit')
        messages.success(request, 'Password should contain at least one digit')
        return redirect('/myadmin/add_chairman/')
    elif not any(char.isupper() for char in password):
        print('Password should contain at least one uppercase letter')
        messages.success(request, 'Password should contain at least one uppercase letter')
        return redirect('/myadmin/add_chairman/')
    elif not any(char.islower() for char in password):
        print('Password should contain at least one lowercase letter')
        messages.success(request, 'Password should contain at least one lowercase letter')
        return redirect('/myadmin/add_chairman/')

    # Create user and chairman objects
    user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
    Chairman.objects.create(gender=gender, phone=phone, reg_date=date.today(), user_id=user.id)

    return redirect('/myadmin/dashboard/')

@login_required(login_url='/myadmin/login/')
def view_chairman(request):
    result = User.objects.all()
    result2 = Chairman.objects.all()
    context = {'result':result, 'result2':result2}

    return render(request, 'myadmin/view_chairman.html', context)

@login_required(login_url='/myadmin/login/')
def edit_chairman(request,id):
    result = Chairman.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'myadmin/edit_chairman.html', context)

def update_chairman(request,id):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']

    gender = request.POST['gender']
    phone = request.POST['phone']

    result_2 = Chairman.objects.get(pk=id)
    table_id = result_2.user_id

    print(table_id)
    
    data = {
            'first_name' : first_name,
            'last_name' : last_name,
            'username' : username,
            'email' : email
        }
    user = User.objects.update_or_create(pk=table_id,defaults=data)

    data2 = {
            'gender' : gender,
            'phone' : phone,
        }
    Chairman.objects.update_or_create(pk=id,defaults=data2)

    return redirect('/myadmin/view_chairman/')


@login_required(login_url='/myadmin/login/')
def remove_chairman(request, id):
    result = Chairman.objects.get(pk=id)
    result.delete()

    return redirect('/myadmin/add_chairman/')

@login_required(login_url='/myadmin/login/')
def view_member(request):
    result = Member.objects.all()
    context = {'result':result}

    return render(request, 'myadmin/view_member.html', context)

@login_required(login_url='/myadmin/login/')
def member_details(request, id):
    result = Member.objects.get(pk=id)

    context = {'result':result, 'id':id}
    return render(request, 'myadmin/member_details.html', context)

@login_required(login_url='/myadmin/login/')
def remove_member(request, id):
    result = Member.objects.get(pk=id)
    result2 = User.objects.get(pk=result.user_id)
    # print(result2.first_name)
    # print(result.house_no)
    result.delete()
    result2.delete()

    return redirect('/myadmin/view_member/')

@login_required(login_url='/myadmin/login/')
def all_complaints(request):
    result = Complain.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/all_complaints.html', context)

@login_required(login_url='/myadmin/login/')
def all_events(request):
    result = Event.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/all_events.html', context)

def remove_event(request, id):
    result = Event.objects.get(pk=id)
    print(result.title)
    result.delete()
    return redirect('/myadmin/all_events/')

@login_required(login_url='/myadmin/login/')
def all_maintenance(request):
    result = Maintenance.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/all_maintenance.html', context)

@login_required(login_url='/myadmin/login/')
def all_meeting(request):
    result = Meeting.objects.all()
    context = {'result':result}
    return render(request, 'myadmin/all_meeting.html', context)

def remove_meeting(request, id):
    result = Meeting.objects.get(pk=id)
    print(result.subject)
    result.delete()
    return redirect('/myadmin/all_meeting/')

@login_required(login_url='/myadmin/login/')
def complaint_details(request, id):
    result = Complain.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'myadmin/complaint_details.html', context)

@login_required(login_url='/myadmin/login/')
def paid_maintenance(request):
    result = Maintenance_Payment.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/paid_maintenance.html', context)

@login_required(login_url='/myadmin/login/')
def paid_maintenance_details(request,id):
    result = Maintenance_Payment.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'myadmin/paid_maintenance_details.html', context)

@login_required(login_url='/myadmin/login/')
def customer_report(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        
        if not from_date_str or not to_date_str:
            messages.error(request, 'Please provide both from and to dates.')
            return redirect('/myadmin/customer_report/')  # Redirect to the appropriate view
            
        # Parsing the dates to ensure they are in the correct format
        try:
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
            return redirect('/myadmin/customer_report/')  # Redirect to the appropriate view
        
        result = Member.objects.filter(reg_date__gte=from_date, reg_date__lte=to_date)
        request.session['from_date'] = from_date_str
        request.session['to_date'] = to_date_str
        
        if result.exists():
            context = {'user': result, 'f': from_date_str, 't': to_date_str}
        else:
            context = {'user': None}
    else:
        context = {'user': Member.objects.all()}
        
    return render(request, 'myadmin/customer_report.html', context)

#Creating a class based view
class GeneratePdf(View):
    
     def get(self, request, *args, **kwargs):
        from_date = request.session['from_date']
        to_date   = request.session['to_date']

        data = Member.objects.filter(reg_date__gte=from_date,reg_date__lte=to_date)
        cdate = date.today()
        cdate1 = cdate.strftime('%d/%m/%Y')
        open('templates/temp.html', "w").write(render_to_string('result.html', {'data': data,'current_date':cdate1}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf('temp.html')
         
         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')

@login_required(login_url='/myadmin/login/')
def maintenance_report(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        
        if not from_date_str or not to_date_str:
            messages.error(request, 'Please provide both from and to dates.')
            return redirect('/myadmin/maintenance_report/')  # Redirect to the appropriate view
            
        # Parsing the dates to ensure they are in the correct format
        try:
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
            return redirect('/myadmin/maintenance_report/')  # Redirect to the appropriate view
        
        result = Maintenance_Payment.objects.filter(date__gte=from_date, date__lte=to_date)
        request.session['from_date'] = from_date_str
        request.session['to_date'] = to_date_str
        
        if result.exists():
            context = {'user': result, 'f': from_date_str, 't': to_date_str}
        else:
            context = {'user': None}
    else:
        context = {'user': Maintenance_Payment.objects.all()}
        
    return render(request, 'myadmin/maintenance_report.html', context)

#Creating a class based view
class GeneratePdf2(View):
    
     def get(self, request, *args, **kwargs):
        from_date = request.session['from_date']
        to_date   = request.session['to_date']
        data = Maintenance_Payment.objects.filter(date__gte=from_date,date__lte=to_date)
        cdate = date.today()
        cdate1 = cdate.strftime('%d/%m/%Y')
        open('templates/temp.html', "w").write(render_to_string('maintenance.html', {'data': data,'current_date':cdate1}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf('temp.html')
         
         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')

@login_required(login_url='/myadmin/login/')
def event_report(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        
        if not from_date_str or not to_date_str:
            messages.error(request, 'Please provide both from and to dates.')
            return redirect('/myadmin/event_report/')  # Redirect to the appropriate view
            
        # Parsing the dates to ensure they are in the correct format
        try:
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
            return redirect('/myadmin/event_report/')  # Redirect to the appropriate view
        
        result = Event_Payment.objects.filter(date__gte=from_date, date__lte=to_date)
        request.session['from_date'] = from_date_str
        request.session['to_date'] = to_date_str
        
        if result.exists():
            context = {'user': result, 'f': from_date_str, 't': to_date_str}
        else:
            context = {'user': None}
    else:
        context = {'user': Event_Payment.objects.all()}
        
    return render(request, 'myadmin/event_report.html', context)

#Creating a class based view
class GeneratePdf3(View):
    
     def get(self, request, *args, **kwargs):
        from_date = request.session['from_date']
        to_date   = request.session['to_date']
        data = Event_Payment.objects.filter(date__gte=from_date,date__lte=to_date)
        cdate = date.today()
        cdate1 = cdate.strftime('%d/%m/%Y')
        open('templates/temp.html', "w").write(render_to_string('event.html', {'data': data,'current_date':cdate1}))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf('temp.html')
         
         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')