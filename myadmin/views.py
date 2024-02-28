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
        auth.login(request, result)
        return redirect('/myadmin/dashboard/')

def logout(request):

    print(request.user.id)
    auth.logout(request)
    print(request.user.id)
    return redirect('/myadmin/login/')

def dashboard(request):
    print(request.user.id)
    context={}
    return render(request, 'myadmin/dashboard.html', context)

def add_chairman(request):
    context={}
    return render(request, 'myadmin/add_chairman.html', context)

def store_chairman(request):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    password = request.POST['password']
    cpassword = request.POST['cpassword']
    email = request.POST['email']

    gender = request.POST['gender']
    phone = request.POST['phone']

    if password == cpassword:
        user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)

        Chairman.objects.create(gender=gender,phone=phone,reg_date=date.today(),user_id=user.id)
        return redirect('/myadmin/dashboard/')

    else:
        print('Password and confirm password mismatched')

def view_chairman(request):
    result = User.objects.all()
    result2 = Chairman.objects.all()
    context = {'result':result, 'result2':result2}

    return render(request, 'myadmin/view_chairman.html', context)

def remove_chairman(request, id):
    result = Chairman.objects.get(pk=id)
    result.delete()

    return redirect('/myadmin/add_chairman/')

def view_member(request):
    result = Member.objects.all()
    context = {'result':result}

    return render(request, 'myadmin/view_member.html', context)

def member_details(request, id):
    result = Member.objects.get(pk=id)

    context = {'result':result, 'id':id}
    return render(request, 'myadmin/member_details.html', context)

def remove_member(request, id):
    result = Member.objects.get(pk=id)
    result2 = User.objects.get(pk=result.user_id)
    # print(result2.first_name)
    # print(result.house_no)
    result.delete()
    result2.delete()

    return redirect('/myadmin/view_member/')

    

def all_complaints(request):
    result = Complain.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/all_complaints.html', context)

def all_events(request):
    result = Event.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/all_events.html', context)

def all_maintenance(request):
    result = Maintenance.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/all_maintenance.html', context)

def all_meeting(request):
    result = Meeting.objects.all()
    context = {'result':result}
    return render(request, 'myadmin/all_meeting.html', context)

def complaint_details(request, id):
    result = Complain.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'myadmin/complaint_details.html', context)

def paid_maintenance(request):
    result = Maintenance_Payment.objects.all()

    context = {'result':result}
    return render(request, 'myadmin/paid_maintenance.html', context)

def paid_maintenance_details(request,id):
    result = Maintenance_Payment.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'myadmin/paid_maintenance_details.html', context)

def customer_report(request):
    if request.method =='POST':
        from_date = request.POST['from_date']
        to_date   = request.POST['to_date']
        result = Member.objects.filter(reg_date__gte=from_date,reg_date__lte=to_date)
        request.session['from_date'] = from_date
        request.session['to_date'] = to_date
        if result.exists():
            context = {'user':result,'f':from_date,'t':to_date} 
        else:
            context = {'user':None} 
    else:
        context = {'user':Member.objects.all()}
    return render(request,'myadmin/customer_report.html',context)

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

def maintenance_report(request):
    if request.method =='POST':
        from_date = request.POST['from_date']
        to_date   = request.POST['to_date']
        result = Maintenance_Payment.objects.filter(date__gte=from_date,date__lte=to_date)
        request.session['from_date'] = from_date
        request.session['to_date'] = to_date
        if result.exists():
            context = {'user':result,'f':from_date,'t':to_date} 
        else:
            context = {'user':None} 
    else:
        context = {'user':Maintenance_Payment.objects.all()}
    return render(request,'myadmin/maintenance_report.html',context)

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

def event_report(request):
    if request.method =='POST':
        from_date = request.POST['from_date']
        to_date   = request.POST['to_date']
        result = Event_Payment.objects.filter(date__gte=from_date,date__lte=to_date)
        request.session['from_date'] = from_date
        request.session['to_date'] = to_date
        if result.exists():
            context = {'user':result,'f':from_date,'t':to_date} 
        else:
            context = {'user':None} 
    else:
        context = {'user':Event_Payment.objects.all()}
    return render(request,'myadmin/event_report.html',context)

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