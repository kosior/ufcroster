from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView

from .models import Fighter, Fight, FightDetails


class CountryCodeMixin:
    def get_country_code(self):
        country_code = self.kwargs.get('country_code', '')
        if country_code in settings.COUNTRIES_URL_CODES:
            return country_code.upper()
        raise Http404


class IndexView(TemplateView):
    template_name = 'index.html'


class FighterDetail(DetailView):
    model = Fighter
    queryset = Fighter.objects.full_fighter()
    context_object_name = 'fighter'


class UpcomingFightsByCountry(CountryCodeMixin, ListView):
    context_object_name = 'fights'
    template_name = 'fighters/upcoming_by_country.html'

    def get_queryset(self):
        return Fight.objects.filter(details__status=FightDetails.UPCOMING, fighter__country=self.get_country_code())


class FightersByCountry(CountryCodeMixin, ListView):
    context_object_name = 'fighters'
    template_name = 'fighters/fighters.html'

    def get_queryset(self):
        in_ufc = 'released' not in self.request.GET.keys()
        return Fighter.objects.by_country(self.get_country_code()).filter(in_ufc=in_ufc)
