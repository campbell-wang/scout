from django.contrib import admin
from .models import Issuer, Card, Subscriber, Subscription

admin.site.register(Issuer)
admin.site.register(Card)
admin.site.register(Subscriber)
admin.site.register(Subscription)