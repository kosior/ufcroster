from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView

from .models import Fighter, Fight


class CountryCodeMixin:
    def get_country_code(self):
        country_code = self.kwargs.get('country_code', '').upper()
        if country_code in settings.COUNTRIES_URL_CODES:
            return country_code
        raise Http404


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fights_qs = Fight.objects.upcoming().fight_with_relations()
        context['closest_fights'] = fights_qs.order_by('details__date')[:5]
        context['recently_added_fights'] = fights_qs.order_by('-created')[:5]
        context['recently_created_fighters'] = Fighter.objects.details().active().order_by('-created')[:5]
        return context


class FighterDetail(DetailView):
    model = Fighter
    queryset = Fighter.objects.details()
    context_object_name = 'fighter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fights_list'] = Fight.objects.fight_with_relations().filter(fighter=self.object)
        return context


class UpcomingFightsByCountry(CountryCodeMixin, ListView):
    context_object_name = 'fights'
    template_name = 'fighters/upcoming_by_country.html'

    def get_queryset(self):
        return Fight.objects.upcoming_by_country(self.get_country_code()).order_by('details__date')


class FightersByCountry(CountryCodeMixin, ListView):
    context_object_name = 'fighters'
    template_name = 'fighters/fighters.html'

    def get_queryset(self):
        in_ufc = 'released_retired' not in self.request.GET.keys()
        return Fighter.objects.by_country(self.get_country_code()).filter(in_ufc=in_ufc)
