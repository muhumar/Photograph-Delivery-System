from __future__ import unicode_literals
from django.db import models
from django.template.loader import render_to_string
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.core.urlresolvers import reverse
from datetime import datetime
# import datetime
import stripe

def upload_location(instance, filename):
    return "%s/%s" %(instance.id, filename)


class Profile(models.Model):
    username = models.CharField(max_length=200)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', editable=False, null=True)
    note = models.TextField(max_length=500, blank=True, help_text="Want to say something to customer")
    is_allowed = models.BooleanField(default=False)
    amount = models.FloatField(default=5, help_text="Enter amount in dollars")
    drive_url = models.CharField(max_length=200, blank=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)
    client_token = models.CharField(max_length=120, null=True, blank=True)
    image1 = models.ImageField(upload_to=upload_location, blank=True, null=True)
    image2 = models.ImageField(upload_to=upload_location, blank=True, null=True)
    image3 = models.ImageField(upload_to=upload_location, blank=True, null=True)
    image4 = models.ImageField(upload_to=upload_location, blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("profile", kwargs={"username": self.user.username})

class ChargeManager(models.Manager):
    def do(self,profile,card=None):
       c = stripe.Charge.create(
            amount = int(profile.amount * 100),
            currency = 'usd',
            customer = profile.customer_id,
            source = card.stripe_id,
            description = str(profile.note)
        )
       new_charge_obj = self.model(
            email = profile.email,
            stripe_id = c.id,
            paid = c.paid,
            refunded = c.refunded,
            outcome = c.outcome,
            outcome_type = c.outcome['type'],
            seller_message = c.outcome.get('seller_message'),
            risk_level = c.outcome.get('risk_level')
        )
       new_charge_obj.save()
       return new_charge_obj.paid,new_charge_obj.seller_message

class Charge(models.Model):
    email = models.EmailField()
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True,blank=True)
    outcome_type = models.CharField(max_length=120,blank=True,null=True)
    seller_message = models.CharField(max_length=120,null=True,blank=True)
    risk_level = models.CharField(max_length=120,null=True,blank=True)

    objects = ChargeManager()


class Order(models.Model):
    profile_name = models.CharField(max_length=200)
    profile_email = models.CharField(max_length=200)
    profile_amount = models.IntegerField()
    date = models.DateTimeField(default=datetime.now(), blank=True)

    def __str__(self):
        return self.profile_name




@receiver(post_save, sender=Profile)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        current_site = 'http://127.0.0.1:8000'
        subject = "Account Activation"
        user = User(username=instance.username,email=instance.email, is_active=False)
        user.set_password(str(instance.password))
        user.profile = instance
        user.save()
        subject = 'Activate Your {} Account'.format(current_site)
        message_txt = render_to_string('registration/account_activation_email.txt', {
            'user': user,
            'Subject': subject,
            'password': instance.password,
            'email': instance.email,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        message_html = render_to_string('registration/account_activation_email.html', {
            'user': user,
            'Subject': subject,
            'password': instance.password,
            'email': instance.email,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message_txt, 'heritagemedianetwork@gmail.com', html_message=message_html)
        instance.user = user
        instance.save()
    instance.user.save()


@receiver(post_delete, sender=Profile)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user: # just in case user is not specified
        instance.user.delete()