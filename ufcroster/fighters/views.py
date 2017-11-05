from django.views.generic import DetailView

from .models import Fighter


class FighterDetail(DetailView):
    model = Fighter
    queryset = Fighter.objects.full_fighter()
    context_object_name = 'fighter'
