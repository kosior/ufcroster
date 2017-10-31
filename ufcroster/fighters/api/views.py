from rest_framework import viewsets

from .serializers import FighterSerializer
from ..models import Fighter


class FighterViewSet(viewsets.ModelViewSet):
    queryset = Fighter.objects.details()
    serializer_class = FighterSerializer
    lookup_field = 'slug'
