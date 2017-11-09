from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .serializers import FighterSerializer, FightSerializer
from ..models import Fighter, Fight


class FighterViewSet(viewsets.ModelViewSet):
    queryset = Fighter.objects.details()
    serializer_class = FighterSerializer
    lookup_field = 'slug'


class FightViewSet(viewsets.ModelViewSet):
    serializer_class = FightSerializer

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']
            if isinstance(data, list):
                kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        fighter = get_object_or_404(Fighter, slug=slug)
        return Fight.objects.full_fights(fighter=fighter)
