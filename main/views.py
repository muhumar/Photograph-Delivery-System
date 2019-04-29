from django.shortcuts import render_to_response, get_object_or_404,render,redirect
from django.http import HttpResponse, Http404
from .models import Category, PortfolioImages, AboutMe
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from account.models import Profile, Order
from django.core.mail import send_mail, BadHeaderError,EmailMessage
from .forms import ContactForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.db.models.signals import pre_save
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.contrib.auth.models import User
from django.utils.http import is_safe_url
from django.contrib.auth.decorators import login_required
from django.conf import settings
from account.models import Charge
import stripe

# stripe.api_key = "sk_live_TPfQtQLZYzR3yMskwIvFJ9Bi"
#
# STRIPE_PUB_KEY = "pk_live_wMwikXcsfnXy6rSkKlaQmAZP"
stripe.api_key = "sk_test_P4xBmyb84tYPe0zbLXcMaYUl"

STRIPE_PUB_KEY = "pk_test_sKrTiEjnIX8gipgtdTcc9LJw"


def stripe_profile_created_receiver(sender,instance,*args,**kwargs):
    if not instance.customer_id:
        print("API request sent to Stripe.")
        customer = stripe.Customer.create(
            email=instance.email
        )
        print(customer)
        instance.customer_id = customer.id


pre_save.connect(stripe_profile_created_receiver, sender=Profile)


@csrf_exempt
def payment_method_view(request):
    next_url = '/'
    next_ = request.GET.get('next')
    if is_safe_url(next_,request.get_host()):
        next_url = next_
    return render(request, 'payment-method.html', {'publish_key':STRIPE_PUB_KEY,'next_url':next_url})


@csrf_exempt
def payment_method_createview(request):
    host = request.get_host()
    print(request.user)
    profile_obj = get_object_or_404(Profile, user=request.user)
    if request.method == "POST" and request.is_ajax():
        print(request.POST)
        token = request.POST.get('token')
        if token is not None:
            try:
                customer = stripe.Customer.retrieve(profile_obj.customer_id)
                print(profile_obj.note,'Note')
                card_response = customer.sources.create(source=token)
                print(card_response)
                did_chrg, chrg_message = Charge.objects.do(profile_obj,card_response)
                if did_chrg:
                    profile_obj.is_allowed = True
                    profile_obj.save()
                    print("paid")
                    email_body = 'Thank you for choosing Heritage Media Network. We are delighted to partner with you in the marketing of your listing. Below you will find the details of your purchase. Good luck with the sale of your property \n {details}'.format(details=profile_obj.note)
                    sending_payment_email = EmailMessage('Payment Successful',email_body,settings.EMAIL_HOST_USER,[profile_obj.email])
                    sending_payment_email.send()
                    return JsonResponse({'message': 'Success! You card was processed. Payment Done. Redirecting... '})
                else:
                    print("Error")
            except stripe.error.CardError as e:
                print("Card Declined.")
                return JsonResponse({'message': 'Your card was declined.'})
    return render(request, 'payment-method.html', {'publish_key': STRIPE_PUB_KEY})


def home(request):
    category_objects = Category.objects.all()
    specialties = Category.objects.order_by('?')[:3]
    portfolio_objects = PortfolioImages.objects.all()
    about_me = AboutMe.objects.first()
    return render(request,"base.html",{"category_objects":category_objects, "portfolio_objects":portfolio_objects,
                                       "specialties": specialties, "about_me": about_me})


def about(request):
    about_me = AboutMe.objects.first()
    return render(request,"about.html",{"about_me": about_me})

def privacy(request):
    return render(request,"privacy.html")

def portfolio(request):
    about_me = AboutMe.objects.first()
    portfolio_objects = PortfolioImages.objects.all()
    return render(request,"portfolio.html",{"portfolio_objects": portfolio_objects, "about_me": about_me})


def category(request, slug):
    about_me = AboutMe.objects.first()
    category_object = get_object_or_404(Category, slug=slug)
    if category_object:
        category_portfolio_objects = PortfolioImages.objects.filter(category=category_object)
        return render(request, "portfolio.html", {"all_objects": category_portfolio_objects, "about_me": about_me})
    else:
        return Http404


def paypal_home(request):
    context = {}
    host = request.get_host()
    profile_obj = get_object_or_404(Profile, user=request.user)
    paypal_dict = {
        'business':'heritagemedianetwork@gmail.com',
        'amount':profile_obj.amount,
        'User': 'UserName {}'.format(request.user.username),
        'currency_code':'USD',
        'item_name':'Photographs',
        'invoice': str(profile_obj.id),
        'notify_url':'http://{}{}'.format(host,'/a-very-hard-to-guess-url'),
        'return_url':'http://{}{}'.format(host, '/paypal-return/'),
        'cancel_return':'http://{}{}'.format(host, '/paypal-cancel'),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context['form'] = form
    return render_to_response('paypal_home.html',context)


@csrf_exempt
def paypal_return(request):
    context = {'post':request.POST,'get':request.GET}
    user_obj = User.objects.get(pk=request.user.id)
    user_obj.profile.is_allowed = True
    user_obj.profile.save()
    Name = user_obj.username
    Email = user_obj.email
    Amount = user_obj.profile.amount
    order = Order(profile_name=Name,profile_email=Email, profile_amount = Amount)
    order.save()
    current_site = get_current_site(request)
    #to_email = 'heritagemedianetwork@gmail.com'
    to_email = 'muhumar77@gmail.com'
    msg_mail = 'You have received an amount'
    message_html = render_to_string('email_for_received_amount.html', {
        'Name': Name,
        'profile_amount': Amount,
        'profile_name': Name,
        'profile_email': Email,
        'domain': current_site.domain,
        'message': msg_mail,
    })
    message_html1 = render_to_string('email_payment_confirmation.html', {
        'Name': Name,
        'profile_amount': Amount,
        'profile_name': Name,
        'profile_email': Email,
        'domain': current_site.domain,
        'message': 'you have paid an amount',
    })
    send_mail('Amount received', msg_mail, 'heritagemedianetwork@gmail.com', [to_email], html_message=message_html,)
    send_mail('Amount Paid', msg_mail, 'heritagemedianetwork@gmail.com', [to_email], html_message=message_html1,)
    return render_to_response('paypal_return.html',context)


def paypal_cancel(request):
    context = {'post': request.POST, 'get': request.GET}
    print(context['post'], context['get'])
    return render_to_response('paypal_cancel.html', context)


def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        user_obj = User.objects.get(pk=sender.user.id)
        user_obj.profile.is_allowed = True
        user_obj.profile.save()
    else:
        print("Else")


valid_ipn_received.connect(show_me_the_money)


def email(request):
    if request.method == 'GET':
        form = ContactForm()
        return render(request, "contact.html", {'about': AboutMe.objects.first(),'form': form})
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            phone = form.cleaned_data['phone']
            name = form.cleaned_data['name']
            msg_mail = str(message)
            current_site = get_current_site(request)
            to_email = 'heritagemedianetwork@gmail.com'
            message_txt = render_to_string('email.txt', {
                'Name': name,
                'Phone': phone,
                'Subject': subject,
                'To_Email': to_email,
                'From_Email': from_email,
                'domain': current_site.domain,
                'message': msg_mail,
            })
            message_html = render_to_string('emailFormat.html', {
                'Name': name,
                'Phone': phone,
                'Subject': subject,
                'To_Email': to_email,
                'From_Email': from_email,
                'domain': current_site.domain,
                'message': msg_mail,
            })
            send_mail(
                subject,
                message,
                from_email,
                to_email,
                html_message=message_html,
            )
            form = ContactForm()
            return render(request, "contact.html", {'about':AboutMe.objects.first(),'form': form,'message': "Success"})
    return render(request, "contact.html", {'about': AboutMe.objects.first(), 'form': form})


