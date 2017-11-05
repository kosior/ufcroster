from rest_framework import serializers

from ..models import Event


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'url': {'view_name': 'api:event-detail', 'lookup_field': 'id'},
            'title': {'validators': []}, 'sherdog_url': {'validators': []}
        }
