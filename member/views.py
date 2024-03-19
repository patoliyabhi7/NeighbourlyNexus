from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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
import razorpay
from django.views.decorators.csrf import csrf_exempt
import random
import json

# from razorpay.utils import verify_payment_signature


def login(request):
    context={}
    return render(request, 'member/login.html', context)

def login_check(request):
    username = request.POST['username']
    password = request.POST['password']

    result = auth.authenticate(username=username, password=password)

    if result is None:
        messages.success(request, 'Invalid username or password')
        print('Invalid username or password')
        return redirect('/member/login/')

    else:
        auth.login(request, result)
        return redirect('/member/dashboard/')

def dashboard(request):
    id = request.user.id
    print(id)
    result = User.objects.get(pk=id)
    context={'result' : result}
    return render(request, 'member/dashboard.html', context)

def logout(request):
    auth.logout(request)
    return redirect('/member/login/')

def member_details(request):
    id = request.user.id
    result = Member.objects.get(user_id=id)

    context = {'result':result}
    return render(request, 'member/member_details.html', context)

def all_events(request):
    result = Event.objects.all()

    context = {'result':result}
    return render(request, 'member/all_events.html', context)

def all_meeting(request):
    result = Meeting.objects.all()
    context = {'result':result}
    return render(request, 'member/all_meeting.html', context)

def all_maintenance(request):
    # result = Maintenance.objects.all()
    # result2 = Maintenance_Payment.objects.all()
    # id = request.user.id
    # result3 = Member.objects.get(user_id=id).id
    # print(result3)

    result = Maintenance.objects.all()
    id = request.user.id
    member_data = Member.objects.get(user_id=id)

    for row in result:
        result1 = Maintenance_Payment.objects.filter(maintenance_id=row.id,member_id=member_data.id )
        if result1.exists():
            row.status = 'Paid'
        else:
            row.status = 'Unpaid'

    context = {'result':result}
    return render(request, 'member/all_maintenance.html', context)

def complaint(request):
    
    context = {}
    return render(request, 'member/complaint.html', context)

def post_complaint(request):
    subject = request.POST['subject']
    description = request.POST['description']
    id = request.user.id
    result = Member.objects.get(user_id=id).id

    Complain.objects.create(subject=subject,description=description,date_time=datetime.today(),member_id=result)
    return redirect('/member/complaint/')

def all_complaints(request):
    id = request.user.id
    id1 = Member.objects.get(user_id=id).id
    result = Complain.objects.all()
    
    context = {'result':result, 'id':id1}
    return render(request, 'member/all_complaints.html', context)

def remove_complaint(request, id):
    result = Complain.objects.get(pk=id)
    print(result.subject)
    result.delete()
    return redirect('/member/all_complaints/')

def edit_complaint(request, id):
    result = Complain.objects.get(pk=id)
    print(id)
    context = {'result':result}
    return render(request, 'member/edit_complaint.html', context)

def update_complaint(request, id):
    subject = request.POST['subject']
    description = request.POST['description']

    data = {
                'subject':subject,
                'description': description,
            }

    Complain.objects.update_or_create(pk=id, defaults=data)
    return redirect('/member/all_complaints/')

def edit_profile(request, id):
    result = Member.objects.get(pk=id)
    print(request.user.id)
    context = {'result':result}
    return render(request, 'member/edit_profile.html', context)

def update_profile(request, id):
    print(id)
    id1 = request.user.id

    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']

    gender = request.POST['gender']
    phone = request.POST['phone']
    house_no = request.POST['house_no']
    total_members = request.POST['total_members']

    data = {
            'first_name' : first_name,
            'last_name' : last_name,
            'username' : username,
            'email' : email
        }
    user = User.objects.update_or_create(pk=id1,defaults=data)

    data2 = {
            'gender' : gender,
            'phone' : phone,
            'house_no' : house_no,
            'total_members' : total_members,
        }
    Member.objects.update_or_create(user_id=id,defaults=data2)

    return redirect('/member/member_details/')

def change_password(request):
    id = request.user.id
    result = User.objects.get(pk=id)
    context = {'result' : result}
    return render(request, 'member/change_password.html', context)

def spasse(request):
    username = request.user.username

    old_pass = request.POST['old_pass']
    new_pass = request.POST['new_pass']
    rnew_pass = request.POST['rnew_pass']

    if new_pass == rnew_pass:
        user = auth.authenticate(username=username,password=old_pass)
        if user is not None:
            user.set_password(new_pass)
            user.save()
            return redirect('/member/login/')
        else:
            messages.success(request, 'Invalid current password ')
            print('Invalid Current Password')
            return redirect('/member/change_password/')

    else:
        messages.success(request, 'Password and Confirm Password mismatched')    
        print('Password and Confirm Password mismatched')
        return redirect('/member/change_password/')



def make_payment(request,id):
    key_id = 'rzp_test_qu1r85W33FbFlf'
    key_secret = 'mNX26pRh92aG5BqjlM9LIHLQ'

    # amount = request.POST['amount']
    result2 = Maintenance.objects.get(pk=id)
    amount = result2.amount
    m_id = result2.id

    client = razorpay.Client(auth=(key_id, key_secret))

    data = {
        'amount': amount*100,
        'currency': 'INR',
        "receipt":"Shivam_Casa",
        "notes":{
            'name' : 'Abhi',
            'payment_for':'Payment Test'
        }
    }
    id1 = request.user.id
    print('The id is ',id1)
    result = User.objects.get(pk=id1)
    result2 = Member.objects.get(user_id=id1).phone
    payment = client.order.create(data=data)
    context = {'payment' : payment,'result':result,'result2':result2,'phone':result2, 'm_id':m_id,'the_user_id':id1}
    return render(request, 'member/process_payment.html',context)

@csrf_exempt
def success(request):
    context = {}
    return render(request, 'member/success.html', context)

@csrf_exempt
def r_details(request, id, id2):

    id1 = id
    print(id1)
    result = Member.objects.get(user_id=id1)

    order_id = request.POST.get('razorpay_order_id')
    payment_id = request.POST.get('razorpay_payment_id')
    signature = request.POST.get('razorpay_signature')
    client = razorpay.Client(auth=("rzp_test_qu1r85W33FbFlf", "mNX26pRh92aG5BqjlM9LIHLQ"))
    # print(client.utility.verify_payment_signature)
    
    client.utility.verify_payment_signature({
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    })
    print("Success")
    Maintenance_Payment.objects.create(order_id=order_id,payment_id=payment_id,signature=signature,date=date.today(),date_time=datetime.today(),member_id=result.id,maintenance_id=id2)
    # Payment is successful, do something here
    return redirect('/member/success/')


def paid_maintenance(request):
    id = request.user.id
    result = Member.objects.get(user_id=id).id
    result2 = Maintenance_Payment.objects.all()

    context = {'result2':result2,'result':result}
    return render(request, 'member/paid_maintenance.html', context)




def make_payment_event(request,id):
    key_id = 'rzp_test_qu1r85W33FbFlf'
    key_secret = 'mNX26pRh92aG5BqjlM9LIHLQ'

    # amount = request.POST['amount']
    result2 = Event.objects.get(pk=id)
    amount = result2.price
    m_id = result2.id

    client = razorpay.Client(auth=(key_id, key_secret))

    data = {
        'amount': amount*100,
        'currency': 'INR',
        "receipt":"Shivam_Casa",
        "notes":{
            'name' : 'Abhi',
            'payment_for':'Payment Test'
        }
    }
    id1 = request.user.id
    result = User.objects.get(pk=id1)
    result2 = Member.objects.get(user_id=id1).phone
    payment = client.order.create(data=data)
    context = {'payment' : payment,'result':result,'result2':result2,'phone':result2, 'm_id':m_id}
    return render(request, 'member/process_payment_event.html',context)

@csrf_exempt
def r_details_event(request, id):

    print(id)
    id1 = request.user.id
    result = Member.objects.get(user_id=id1).id

    order_id = request.POST.get('razorpay_order_id')
    payment_id = request.POST.get('razorpay_payment_id')
    signature = request.POST.get('razorpay_signature')
    client = razorpay.Client(auth=("rzp_test_qu1r85W33FbFlf", "mNX26pRh92aG5BqjlM9LIHLQ"))
    # print(client.utility.verify_payment_signature)
    
    client.utility.verify_payment_signature({
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    })
    print("Success")
    Event_Payment.objects.create(order_id=order_id,payment_id=payment_id,signature=signature,date=date.today(),date_time=datetime.today(),member_id=result,event_id=id)
    # Payment is successful, do something here
    return redirect('/member/success/')


def paid_event(request):
    id = request.user.id
    result = Member.objects.get(user_id=id).id
    result2 = Event_Payment.objects.all()

    context = {'result2':result2,'result':result}
    return render(request, 'member/paid_event.html', context)

def get_random_quote(request):
    with open('quotes.json', 'r') as f:
        quotes_data = json.load(f)
    
    random_quote = random.choice(quotes_data)
    # print(random_quote)
    return JsonResponse(random_quote)

def random_thought(request):
    with open('quotes.json') as f:
        thoughts = json.load(f)
    random_thought = random.choice(thoughts)
    return render(request, 'your_template.html', {'thought': random_thought})

def my_view(request):
    random_thought = get_random_thought()  # Function to get a random thought
    print(random_thought)
    return render(request, 'my_template.html', {'thought': random_thought})