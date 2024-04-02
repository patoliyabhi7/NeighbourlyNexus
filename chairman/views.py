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
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_date
from django.core.mail import send_mail

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
            return redirect('/chairman/login/')

        else:
            messages.error(request, 'Invalid User..Try Again')
            return redirect('/chairman/login/')

@login_required(login_url='/chairman/login/')
def dashboard(request):
    id = request.user.id
    print(id)
    result = User.objects.get(pk=id)
    context={'result' : result}
    return render(request, 'chairman/dashboard.html', context)

@login_required(login_url='/chairman/login/')
def logout(request):
    auth.logout(request)
    return redirect('/chairman/login/')

@login_required(login_url='/chairman/login/')
def add_member(request):
    context = {}
    return render(request, 'chairman/add_member.html', context)

@login_required(login_url='/chairman/login/')
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

@login_required(login_url='/chairman/login/')
def view_member(request):
    result = Member.objects.all()
    context = {'result':result}

    return render(request, 'chairman/view_member.html', context)

@login_required(login_url='/chairman/login/')
def member_details(request, id):
    result = Member.objects.get(pk=id)

    context = {'result':result, 'id':id}
    return render(request, 'chairman/member_details.html', context)

@login_required(login_url='/chairman/login/')
def remove_member(request, id):
    result = Member.objects.get(pk=id)
    result2 = User.objects.get(pk=result.user_id)
    # print(result2.first_name)
    # print(result.house_no)
    result.delete()
    result2.delete()

    return redirect('/chairman/view_member/')

@login_required(login_url='/chairman/login/')
def edit_member(request, id):
    result = Member.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'chairman/edit_member.html', context)

@login_required(login_url='/chairman/login/')
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
    user = User.objects.update_or_create(pk=table_id,
    defaults=data)

    data2 = {
            'gender' : gender,
            'phone' : phone,
            'house_no' : house_no,
            'total_members' : total_members,
            'reg_date' : Member.objects.get(pk=id).reg_date
        }
    Member.objects.update_or_create(pk=id, defaults=data2)

    return redirect('/chairman/view_member/')

@login_required(login_url='/chairman/login/')
def add_event(request):

    context = {}
    return render(request, 'chairman/add_event.html', context)

@login_required(login_url='/chairman/login/')
def store_event(request):
    if 'title' not in request.POST or 'description' not in request.POST or 'from_date' not in request.POST or 'to_date' not in request.POST or 'price' not in request.POST or 'image' not in request.FILES:
        messages.success(request, 'All fields are required.')
        return redirect('/chairman/add_event/')

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

    Event.objects.create(title=title, description=description, from_date=from_date, to_date=to_date, price=price, image=image.name)
    request.session['mail_title'] = title
    request.session['mail_description'] = description
    request.session['mail_from_date'] = from_date
    request.session['mail_to_date'] = to_date
    request.session['mail_price'] = price

    send_email_event(request)
    return redirect('/chairman/all_events/')

def send_email_event(request):
    all_members = Member.objects.all()
    mytos = [member.user.email for member in all_members]
    mytitle = request.session['mail_title']
    mydescription = request.session['mail_description']
    myfrom_date = request.session['mail_from_date']
    myto_date = request.session['mail_to_date']
    myprice = request.session['mail_price']

    mymessage = f"Title: {mytitle}\nDescription: {mydescription}\nDate: {myfrom_date} to {myto_date}\nPrice: {myprice}"

    try:
        send_mail(
            mytitle,
            mymessage,
            settings.EMAIL_HOST_USER,
            mytos,
            fail_silently=False
        )
        messages.success(request, 'Email Sent Successfully')
    except Exception as e:
        messages.error(request, f'Error occurred: {str(e)}')
    return redirect('/chairman/add_event/')

@login_required(login_url='/chairman/login/')
def all_events(request):
    result = Event.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_events.html', context)

@login_required(login_url='/chairman/login/')
def remove_event(request, id):
    result = Event.objects.get(pk=id)
    print(result.title)
    result.delete()
    return redirect('/chairman/all_events/')

@login_required(login_url='/chairman/login/')
def edit_event(request, id):
    result = Event.objects.get(pk=id)

    date = Event.objects.get(pk=id).from_date
    from_date = date.strftime("%Y-%m-%d")

    date = Event.objects.get(pk=id).to_date
    to_date = date.strftime("%Y-%m-%d")

    context = {'result':result,'from_date':from_date,'to_date':to_date}
    return render(request, 'chairman/edit_event.html', context)

@login_required(login_url='/chairman/login/')
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

@login_required(login_url='/chairman/login/')
def schedule_meeting(request):

    context = {}
    return render(request, 'chairman/schedule_meeting.html', context)

@login_required(login_url='/chairman/login/')
def store_meeting(request):
    if 'subject' not in request.POST or 'venue' not in request.POST or 'date' not in request.POST or 'time' not in request.POST:
        messages.error(request, 'All fields are required.')
        return redirect('/chairman/schedule_meeting/')

    subject = request.POST['subject']
    venue = request.POST['venue']
    date_str = request.POST['date']
    time_str = request.POST['time']

    if date_str == "" or time_str == "":
        messages.error(request, 'All fields are required.')
        return redirect('/chairman/schedule_meeting/')

    # Combine date and time strings into a datetime object
    meeting_datetime = datetime.strptime(date_str + ' ' + time_str, '%Y-%m-%d %H:%M')

    # Check if the meeting datetime is in the future
    if meeting_datetime <= datetime.now():
        messages.error(request, 'Scheduled date and time must be in the future.')
        return redirect('/chairman/schedule_meeting/')

    request.session['mail_subject'] = subject
    request.session['mail_venue'] = venue
    request.session['mail_date'] = date_str
    request.session['mail_time'] = time_str

    Meeting.objects.create(subject=subject, venue=venue, date=date_str, time=time_str)
    send_email(request)
    return redirect('/chairman/all_meeting/')

def send_email(request):
    all_members = Member.objects.all()
    mytos = [member.user.email for member in all_members]
    mysubject = request.session['mail_subject']
    myvenue = request.session['mail_venue']
    mydate = request.session['mail_date']
    mytime = request.session['mail_time']

    mymessage = f"Subject: {mysubject}\nVenue: {myvenue}\nDate: {mydate}\nTime: {mytime}"

    try:
        send_mail(
            mysubject,
            mymessage,
            settings.EMAIL_HOST_USER,
            mytos,
            fail_silently=False
        )
        messages.success(request, 'Email Sent Successfully')
    except Exception as e:
        messages.error(request, f'Error occurred: {str(e)}')
    return redirect('/chairman/schedule_meeting/')

@login_required(login_url='/chairman/login/')
def all_meeting(request):
    result = Meeting.objects.all()
    context = {'result':result}
    return render(request, 'chairman/all_meeting.html', context)

@login_required(login_url='/chairman/login/')
def remove_meeting(request, id):
    result = Meeting.objects.get(pk=id)
    print(result.subject)
    result.delete()
    return redirect('/chairman/all_meeting/')

@login_required(login_url='/chairman/login/')
def edit_meeting(request, id):
    result = Meeting.objects.get(pk=id)

    # date = Meeting.objects.get(pk=id).date
    # date = date.strftime("%Y-%m-%d")

    context = {'result':result}
    return render(request, 'chairman/edit_meeting.html', context)

@login_required(login_url='/chairman/login/')
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

@login_required(login_url='/chairman/login/')
def add_maintenance(request):

    context = {}
    return render(request, 'chairman/add_maintenance.html', context)

@login_required(login_url='/chairman/login/')
def store_maintenance(request):
    if 'year' not in request.POST or 'from_date' not in request.POST or 'to_date' not in request.POST or 'amount' not in request.POST or 'description' not in request.POST:
        messages.error(request, 'All fields are required.')
        return redirect('/chairman/add_maintenance/')

    year = request.POST['year']
    from_date_str = request.POST['from_date']
    to_date_str = request.POST['to_date']
    amount = request.POST['amount']
    description = request.POST['description']

    if from_date_str == "" or to_date_str == "":
        messages.error(request, 'All fields are required.')
        return redirect('/chairman/add_maintenance/')

    # Convert date strings to datetime objects
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

    # Check if from_date and to_date are in the future
    current_year = datetime.now().year
    if int(year) < current_year or to_date < datetime.now():
        messages.error(request, 'Year and Maintenance dates must be in the future.')
        return redirect('/chairman/add_maintenance/')

    # Check if to_date is after from_date
    if to_date <= from_date:
        messages.error(request, 'End date must be after start date.')
        return redirect('/chairman/add_maintenance/')

    Maintenance.objects.create(year=year, description=description, from_date=from_date_str, to_date=to_date_str, amount=amount)
    request.session['mail_year'] = year
    request.session['mail_description'] = description
    request.session['mail_from_date'] = from_date_str
    request.session['mail_to_date'] = to_date_str
    request.session['mail_amount'] = amount
    send_email_maintenance(request)
    return redirect('/chairman/all_maintenance/')

def send_email_maintenance(request):
    all_members = Member.objects.all()
    mytos = [member.user.email for member in all_members]
    mytitle = "Maintenance"
    mydescription = request.session['mail_description']
    myyear = request.session['mail_year']
    myfrom_date = request.session['mail_from_date']
    myto_date = request.session['mail_to_date']
    myamount = request.session['mail_amount']

    mymessage = f"Title: {mytitle}\nDescription: {mydescription}\nYear: {myyear}\nDate: {myfrom_date} to {myto_date}\nAmount: {myamount}"

    try:
        send_mail(
            mytitle,
            mymessage,
            settings.EMAIL_HOST_USER,
            mytos,
            fail_silently=False
        )
        messages.success(request, 'Email Sent Successfully')
    except Exception as e:
        messages.error(request, f'Error occurred: {str(e)}')
    return redirect('/chairman/add_maintenance/')

@login_required(login_url='/chairman/login/')
def all_maintenance(request):
    result = Maintenance.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_maintenance.html', context)

@login_required(login_url='/chairman/login/')
def remove_maintenance(request, id):
    result = Maintenance.objects.get(pk=id)
    result.delete()
    return redirect('/chairman/all_maintenance/')

@login_required(login_url='/chairman/login/')
def edit_maintenance(request, id):
    result = Maintenance.objects.get(pk=id)
    context = {'result':result}
    return render(request, 'chairman/edit_maintenance.html', context)

@login_required(login_url='/chairman/login/')
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

@login_required(login_url='/chairman/login/')
def all_complaints(request):
    result = Complain.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_complaints.html', context)

@login_required(login_url='/chairman/login/')
def complaint_details(request, id):
    result = Complain.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'chairman/complaint_details.html', context)

@login_required(login_url='/chairman/login/')
def remove_complaint(request, id):
    result = Complain.objects.get(pk=id)
    print(result.subject)
    result.delete()
    return redirect('/chairman/all_complaints/')


@login_required(login_url='/chairman/login/')
def paid_maintenance(request):
    result = Maintenance_Payment.objects.all()

    context = {'result':result}
    return render(request, 'chairman/paid_maintenance.html', context)

@login_required(login_url='/chairman/login/')
def paid_maintenance_details(request,id):
    result = Maintenance_Payment.objects.get(pk=id)

    context = {'result':result}
    return render(request, 'chairman/paid_maintenance_details.html', context)

@login_required(login_url='/chairman/login/')
def search_maintenance(request):
    month = request.POST['month']
    year = request.POST['year']
    result2 = Maintenance_Payment.objects.all()
    context = {'result2':result2,'month':month,'year':year}
    return render(request, 'chairman/search_maintenance.html', context)

@login_required(login_url='/chairman/login/')
def status_maintenance(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        year = request.POST.get('year')
        
        try:
            m = Maintenance.objects.get(year=year)
        except Maintenance.DoesNotExist:
            messages.error(request, f"No Maintenance found for the year {year}")
            return redirect('/chairman/status_maintenance/')  # Provide the appropriate redirect URL

        if status == 'due':
            mp = Maintenance_Payment.objects.only('id').filter(maintenance_id=m.id)
            result = Member.objects.exclude(id__in=mp)
        else:
            result = Maintenance_Payment.objects.filter(maintenance_id=m.id)

        context = {'result': result, 'status': status, 'year': year, 'm': m}
    else:
        context = {}
    return render(request, 'chairman/status_maintenance.html', context)

@login_required(login_url='/chairman/login/')
def customer_report(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        
        if not from_date_str or not to_date_str:
            messages.error(request, 'Please provide both from and to dates.')
            return redirect('/chairman/customer_report/')  # Redirect to the appropriate view
            
        # Parsing the dates to ensure they are in the correct format
        try:
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
            return redirect('/chairman/customer_report/')  # Redirect to the appropriate view
        
        result = Member.objects.filter(reg_date__gte=from_date, reg_date__lte=to_date)
        request.session['from_date'] = from_date_str
        request.session['to_date'] = to_date_str
        
        if result.exists():
            context = {'user': result, 'f': from_date_str, 't': to_date_str}
        else:
            context = {'user': None}
    else:
        context = {'user': Member.objects.all()}
        
    return render(request, 'chairman/customer_report.html', context)

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

@login_required(login_url='/chairman/login/')
def maintenance_report(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        
        if not from_date_str or not to_date_str:
            messages.error(request, 'Please provide both from and to dates.')
            return redirect('/chairman/maintenance_report/')  # Redirect to the appropriate view
            
        # Parsing the dates to ensure they are in the correct format
        try:
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
            return redirect('/chairman/maintenance_report/')  # Redirect to the appropriate view
        
        result = Maintenance_Payment.objects.filter(date__gte=from_date, date__lte=to_date)
        request.session['from_date'] = from_date_str
        request.session['to_date'] = to_date_str
        
        if result.exists():
            context = {'user': result, 'f': from_date_str, 't': to_date_str}
        else:
            context = {'user': None}
    else:
        context = {'user': Maintenance_Payment.objects.all()}
        
    return render(request, 'chairman/maintenance_report.html', context)

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

@login_required(login_url='/chairman/login/')
def event_report(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        
        if not from_date_str or not to_date_str:
            messages.error(request, 'Please provide both from and to dates.')
            return redirect('/chairman/event_report/')  # Redirect to the appropriate view
            
        # Parsing the dates to ensure they are in the correct format
        try:
            from_date = parse_date(from_date_str)
            to_date = parse_date(to_date_str)
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
            return redirect('/chairman/event_report/')  # Redirect to the appropriate view
        
        result = Event_Payment.objects.filter(date__gte=from_date, date__lte=to_date)
        request.session['from_date'] = from_date_str
        request.session['to_date'] = to_date_str
        
        if result.exists():
            context = {'user': result, 'f': from_date_str, 't': to_date_str}
        else:
            context = {'user': None}
    else:
        context = {'user': Event_Payment.objects.all()}
        
    return render(request, 'chairman/event_report.html', context)

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

def add_notice(request):
    context = {}
    return render(request, 'chairman/add_notice.html', context)

def store_notice(request):
    if 'title' not in request.POST or 'description' not in request.POST:
        messages.error(request, 'All fields are required.')
        return redirect('/chairman/add_notice/')

    title = request.POST['title']
    description = request.POST['description']
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not title or not description or not date:
        messages.error(request, 'All fields are required.')
        return redirect('/chairman/add_notice/')

    Snotice.objects.create(title=title, description=description, datetime=current_date)
    print("Notice added successfully")
    return redirect('/chairman/add_notice/')

def all_notices(request):
    result = Snotice.objects.all()

    context = {'result':result}
    return render(request, 'chairman/all_notices.html', context)

def delete_notice(request, id):
    result = Snotice.objects.get(pk=id)
    result.delete()
    return redirect('/chairman/all_notices/')
