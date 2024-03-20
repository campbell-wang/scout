from django.db import models
from django.utils.translation import gettext_lazy as _

class Issuer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Card(models.Model):

    class CardNetwork(models.TextChoices):
        VISA = "V", _("Visa")
        MASTERCARD = "MC", _("Mastercard")
        AMEX = "AMEX", _("American Express")
    
    type = models.CharField(
        max_length=4,
        choices=CardNetwork.choices,
    )

    name = models.CharField(max_length=100)
    issuedBy = models.ForeignKey(Issuer, on_delete=models.CASCADE)

    annualFee = models.PositiveIntegerField()
    currentBonus = models.PositiveIntegerField()
    
    link = models.URLField()

    def __str__(self):
        return self.name

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Subscription(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    # to ensure a subscriber can only subscribe once to a specific card
    class Meta:
        unique_together = ('subscriber', 'card')

    def __str__(self):
        return f"{self.subscriber.email} subscribed to {self.card.name}"