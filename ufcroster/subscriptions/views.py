from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.edit import BaseCreateView

from .forms import SubscriptionForm
from .models import Subscription
from .utils import generate_token


class Subscribe(BaseCreateView):
    model = Subscription
    form_class = SubscriptionForm
    http_method_names = ['post']

    def form_invalid(self, form):
        return JsonResponse({'msg': form.errors.get('email', 'Something went wrong.')})

    def form_valid(self, form):
        form.save()
        return JsonResponse({'msg': 'Thank you for subscribing. Email has been sent to you with activation link.'})


class ActivateSubscription(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if token:
            try:
                subscription = Subscription.objects.get(token=token, is_active=False)
            except Subscription.DoesNotExist:
                messages.error(request, 'Activation link is no longer valid.')
            else:
                subscription.is_active = True
                subscription.token = generate_token(subscription.email, True)  # generating deactivation token
                subscription.save()
                messages.success(request, 'Subscription has been activated.')
        else:
            messages.error(request, 'Token not provided.')

        return redirect('fighters:index')


class DeactivateSubscription(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if token:
            try:
                subscription = Subscription.objects.get(token=token, is_active=True)
            except Subscription.DoesNotExist:
                messages.error(request, 'Deactivation link is no longer valid.')
            else:
                subscription.delete()
                messages.success(request, 'Subscription has been deactivated.')
        else:
            messages.error(request, 'Token not provided.')

        return redirect('fighters:index')
