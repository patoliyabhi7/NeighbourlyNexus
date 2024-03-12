from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
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
from django.template.loader import render_to_string
from .process import html_to_pdf 
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

def login(request):
    context={}
    return render(request, 'chairman/login.html', context)

def login_check(request):
    username = request.POST['username']
    password = request.POST['password']

    result = auth.authenticate(username=username, password=password)

    if result is None:
        messages.success(request, 'Invalid username or password')
        print('Invalid username or password')
        return redirect('/chairman/login/')

    else: 
        if Chairman.objects.filter(user_id=result.id).exists():
            auth.login(request, result)
            return redirect('/chairman/dashboard/')

        elif Member.objects.filter(user_id=result.id).exists():
            messages.error(request, 'Invalid User..Try Again')
            return redirect('/chairman/dashboard/')

        else:
            messages.error(request, 'Invalid User..Try Again')
            return redirect('/chairman/dashboard/')

@login_required(login_url='/chairman/login/')
def dashboard(request):
    id = request.user.id
    print(id)
    result = User.objects.get(pk=id)
    context={'result' : result}
    return render(request, 'chairman/dashboard.html', context)

def logout(request):
    auth.logout(request)
    return redirect('/chairman/login/')

def add_member(request):
    context = {}
    return render(request, 'chairman/add_member.html', context)

def store_member(request):
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    cpassword = request.POST.get('cpassword', '').strip()
    email = request.POST.get('email', '').strip()
    gender = request.POST.get('gender', '').strip()
    phone = request.POST.get('phone', '').strip()

    house_no = request.POST.get('house_no', '').strip()
    total_members = request.POST.get('total_members', '').strip()

    if not (first_name and last_name and username and password and cpassword and email and gender and phone and house_no and total_members):
        # Check if any field is empty
        print('All fields are required.')
        messages.success(request, 'All fields are required.')
        return redirect('/chairman/add_member/')

    if password != cpassword:
        # Check if password and confirm password match
        print('Password and confirm password mismatched')
        messages.success(request, 'Password and confirm password mismatched')
        return redirect('/chairman/add_member/')

    if User.objects.filter(username=username).exists():
        # Check if username already exists
        print('Username already exists')
        messages.success(request, 'Username already exists')
        return redirect('/chairman/add_member/')

    try:
        validate_email(email)
    except ValidationError:
        print('Invalid email address')
        messages.success(request, 'Invalid email address')
        return redirect('/chairman/add_member/')

    # Validate phone number format
    if not re.match(r'^\+?1?\d{9,15}$', phone):
        print('Invalid phone number format')
        messages.success(request, 'Invalid phone number format')
        return redirect('/chairman/add_member/')

    if len(password) < 8:
        print('Password should be at least 8 characters long')
        messages.success(request, 'Password should be at least 8 characters long')
        return redirect('/chairman/add_member/')
    elif not any(char.isdigit() for char in password):
        print('Password should contain at least one digit')
        messages.success(request, 'Password should contain at least one digit')
        return redirect('/chairman/add_member/')
    elif not any(char.isupper() for char in password):
        print('Password should contain at least one uppercase letter')
        messages.success(request, 'Password should contain at least one uppercase letter')
        return redirect('/chairman/add_member/')
    elif not any(char.islower() for char in password):
        print('Password should contain at least one lowercase letter')
        messages.success(request, 'Password should contain at least one lowercase letter')
        return redirect('/chairman/add_member/')

    user = User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
    Member.objects.create(gender=gender,phone=phone,house_no=house_no,total_members=total_members ,reg_date=date.today(),user_id=user.id)

    return redirect('/chairman/view_member/')

def view_member(request):
    result = Member.objects.all()
    context = {'result':result}

    return render(request, 'chairman/view_member.html', context)

def member_details(request, id):
    result = Member.objects.get(pk=id)

    context = {'result':result, 'id':id}
    return render(request, 'chairman/member_details.html', context)

def remove_member(request, id):
    result = Member.objects.get(pk=id)
    result2 = User.objects.get(pk=result.user_id)
    # print(result2.first_name)
    # print(result.house_no)
    result.delete()
    result2.delete()

    return redirect('/chairman/view_member/')

def edit_member(request, id):
    result = Member.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'chairman/edit_member.html', context)

def update_member(request, id):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']

    gender = request.POST['gender']
    phone = request.POST['phone']
    house_no = request.POST['house_no']
    total_members = request.POST['total_members']

    result_2 = Member.objects.get(pk=id)
    table_id = result_2.user_id

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
            'house_no' : house_no,
            'total_members' : total_members,
            'reg_date' : Member.objects.get(pk=id).reg_date
,
        }
    Member.objects.update_or_create(pk=id,defaults=data2)

    return redirect('/chairman/view_member/')

def add_event(request):

    context = {}
    return render(request, 'chairman/add_event.html', context)

def store_event(request):
    if 'title' not in request.POST or 'description' not in request.POST or 'from_date' not in request.POST or 'to_date' not in request.POST or 'price' not in request.POST or 'image' not in request.FILES:
        return HttpResponseBadRequest("Missing required fields")

    title = request.POST['title']
    description = request.POST['description']
    from_date = request.POST['from_date']
    to_date = request.POST['to_date']
    price = request.POST['price']

    if not title or not description or not from_date or not to_date or not price:
        return HttpResponseBadRequest("Empty values are not allowed")

    try:
        image = request.FILES['image']
    except KeyError:
        return HttpResponseBadRequest("Image file is missing")

    if not image.name:
        return HttpResponseBadRequest("Image file name is missing")

    myloc = os.path.join(settings.MEDIA_ROOT, 'chairman')
    obj = FileSystemStorage(location=myloc)

    try:
        obj.save(image.name, image)
    except Exception as e:
        return HttpResponseBadRequest("Error saving image file: " + str(e))

    try:
        Event.objects.create(title=title, description=description, from_date=from_date, to_date=to_date, price=price, image=image.name)
    except Exception as e:
        return HttpResponseBadRequest("Error creating event: " + str(e))

    return redirect('/chairman/all_events/')

def all_events(request):
    result = Event.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_events.html', context)

def remove_event(request, id):
    result = Event.objects.get(pk=id)
    print(result.title)
    result.delete()
    return redirect('/chairman/all_events/')

def edit_event(request, id):
    result = Event.objects.get(pk=id)

    date = Event.objects.get(pk=id).from_date
    from_date = date.strftime("%Y-%m-%d")

    date = Event.objects.get(pk=id).to_date
    to_date = date.strftime("%Y-%m-%d")

    context = {'result':result,'from_date':from_date,'to_date':to_date}
    return render(request, 'chairman/edit_event.html', context)

def update_event(request, id):
    title = request.POST['title']
    description = request.POST['description']
    from_date = request.POST['from_date']
    to_date = request.POST['to_date']
    price = request.POST['price']

    image = request.FILES['image']
    myloc = os.path.join(settings.MEDIA_ROOT, 'chairman')
    obj = FileSystemStorage(location=myloc)
    obj.save(image.name, image)

    data = {
                'title':title,
                'description': description,
                'from_date':from_date,
                'to_date':to_date,
                'price':price,
                'image' : image.name,
        }

    Event.objects.update_or_create(pk=id, defaults=data)
    return redirect('/chairman/all_events/')

def schedule_meeting(request):

    context = {}
    return render(request, 'chairman/schedule_meeting.html', context)

def store_meeting(request):
    subject = request.POST['subject']
    venue = request.POST['venue']
    date = request.POST['date']
    time = request.POST['time']

    Meeting.objects.create(subject=subject, venue=venue, date=date, time=time)
    return redirect('/chairman/all_meeting/')

def all_meeting(request):
    result = Meeting.objects.all()
    context = {'result':result}
    return render(request, 'chairman/all_meeting.html', context)

def remove_meeting(request, id):
    result = Meeting.objects.get(pk=id)
    print(result.subject)
    result.delete()
    return redirect('/chairman/all_meeting/')

def edit_meeting(request, id):
    result = Meeting.objects.get(pk=id)

    # date = Meeting.objects.get(pk=id).date
    # date = date.strftime("%Y-%m-%d")

    context = {'result':result}
    return render(request, 'chairman/edit_meeting.html', context)

def update_meeting(request, id):
    subject = request.POST['subject']
    venue = request.POST['venue']
    date = request.POST['date']
    time = request.POST['time']

    data = {
                'subject':subject,
                'venue': venue,
                'date':date,
                'time':time
        }

    Meeting.objects.update_or_create(pk=id, defaults=data)
    return redirect('/chairman/all_meeting/')

def add_maintenance(request):

    context = {}
    return render(request, 'chairman/add_maintenance.html', context)

def store_maintenance(request):
    year = request.POST['year']
    from_date = request.POST['from_date']
    to_date = request.POST['to_date']
    amount = request.POST['amount']
    description = request.POST['description']

    Maintenance.objects.create(year=year,description=description,from_date=from_date,to_date=to_date,amount=amount)

    return redirect('/chairman/all_maintenance/')

def all_maintenance(request):
    result = Maintenance.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_maintenance.html', context)

def remove_maintenance(request, id):
    result = Maintenance.objects.get(pk=id)
    result.delete()
    return redirect('/chairman/all_maintenance/')

def edit_maintenance(request, id):
    result = Maintenance.objects.get(pk=id)
    context = {'result':result}
    return render(request, 'chairman/edit_maintenance.html', context)

def update_maintenance(request, id):
    year = request.POST['year']
    from_date = request.POST['from_date']
    to_date = request.POST['to_date']
    amount = request.POST['amount']
    description = request.POST['description']

    data = {
                'year' : year,
                'from_date' : from_date,
                'to_date' : to_date,
                'amount' : amount,
                'description' : description,
            }
    Maintenance.objects.update_or_create(pk=id, defaults=data)
    return redirect('/chairman/all_maintenance/')

def all_complaints(request):
    result = Complain.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_complaints.html', context)

def complaint_details(request, id):
    result = Complain.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'chairman/complaint_details.html', context)

def remove_complaint(request, id):
    result = Complain.objects.get(pk=id)
    print(result.subject)
    result.delete()
    return redirect('/chairman/all_complaints/')


def paid_maintenance(request):
    result = Maintenance_Payment.objects.all()

    context = {'result':result}
    return render(request, 'chairman/paid_maintenance.html', context)

def paid_maintenance_details(request,id):
    result = Maintenance_Payment.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'chairman/paid_maintenance_details.html', context)

def search_maintenance(request):
    month = request.POST['month']
    year = request.POST['year']
    result2 = Maintenance_Payment.objects.all()
    context = {'result2':result2,'month':month,'year':year}
    return render(request, 'chairman/search_maintenance.html', context)

def status_maintenance(request):
    if request.method == 'POST':
        status = request.POST['status']
        year = request.POST['year']
        m = Maintenance.objects.get(year=year)
        
        if status == 'due':
            mp = Maintenance_Payment.objects.only('id').filter(maintenance_id=m.id)
            result = Member.objects.exclude(id__in=mp)

        else:
            result = Maintenance_Payment.objects.filter(maintenance_id=m.id)

        context = {'result':result, 'status':status,'year':year,'m':m}
    else:
        context = {}
    return render(request, 'chairman/status_maintenance.html', context)




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
    return render(request,'chairman/customer_report.html',context)

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
    return render(request,'chairman/maintenance_report.html',context)

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
    return render(request,'chairman/event_report.html',context)

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