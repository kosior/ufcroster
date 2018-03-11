from django.forms import ModelForm, ValidationError

from .models import Subscription


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ('email', )

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            subscription = Subscription.objects.get(email=email)
        except Subscription.DoesNotExist:
            return email
        else:
            if subscription.is_active:
                raise ValidationError('You have already subscribed.')
            if not subscription.is_active and subscription.token:
                raise ValidationError('Activation link already sent.')
            raise ValidationError('Please contact admin@ufcroster.com')
