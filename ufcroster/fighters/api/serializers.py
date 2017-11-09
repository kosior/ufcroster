from rest_framework import serializers

from common.utils import restructure_fields_by_template
from events.api.serializers import EventSerializer
from events.models import Event
from ..models import Fighter, FighterUrls, FighterRecord, Fight, FightDetails


class FieldsByTemplateMixin:
    fields_template = None

    def __init__(self, *args, **kwargs):
        fields_template = kwargs.pop('fields_template', None) or self.fields_template
        super().__init__(*args, **kwargs)
        if isinstance(fields_template, dict):
            restructure_fields_by_template(self, fields_template)


class FighterUrlsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FighterUrls
        exclude = ('id', 'fighter')
        extra_kwargs = {
            'sherdog': {'validators': []}
        }


class FighterRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FighterRecord
        exclude = ('id', 'fighter')


class FighterSerializer(serializers.HyperlinkedModelSerializer):
    urls = FighterUrlsSerializer()
    record = FighterRecordSerializer()

    class Meta:
        model = Fighter
        fields = '__all__'
        extra_fields = ('urls', 'record')
        extra_kwargs = {
            'url': {'view_name': 'api:fighter-detail', 'lookup_field': 'slug'},
        }

    def create(self, validated_data):
        urls = validated_data.pop('urls')
        record = validated_data.pop('record')
        fighter = super().create(validated_data)
        urls.update(fighter=fighter)
        record.update(fighter=fighter)
        FighterUrlsSerializer().create(urls)
        FighterRecordSerializer().create(record)
        return fighter

    def update(self, instance, validated_data):
        urls = validated_data.pop('urls', None)
        record = validated_data.pop('record', None)
        fighter = super().update(instance, validated_data)
        if urls:
            FighterUrlsSerializer().update(fighter.urls, urls)
        if record:
            FighterRecordSerializer().update(fighter.record, record)
        return fighter


class FightDetailsSerializer(FieldsByTemplateMixin, serializers.ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = FightDetails
        fields = '__all__'
        extra_fields = ('event',)


class FighterFightSerializer(FieldsByTemplateMixin, FighterSerializer):
    fields_template = {
        'name': None,
        'urls': {
            'sherdog': None,
        }
    }


class FightSerializer(serializers.ModelSerializer):
    details = FightDetailsSerializer()
    opponent = FighterFightSerializer()

    class Meta:
        model = Fight
        exclude = ('fighter',)
        extra_fields = ('opponent', 'details')

    def _get_slug(self):
        try:
            slug = self.context.get('view').kwargs.get('slug')
        except AttributeError:
            slug = self.context.get('slug')
        finally:
            if not slug:
                raise ValueError('Slug is none')
            return slug

    def _single_create(self, fighter, validated_data):
        opponent_data = validated_data.pop('opponent')
        details_data = validated_data.pop('details')
        event_data = details_data.pop('event')

        opponent, _ = Fighter.objects.rest_get_or_create(**opponent_data)
        event, _ = Event.objects.get_or_create(**event_data)
        fight_details, _ = FightDetails.objects.get_or_create(event=event, **details_data)

        fight = Fight.objects.create(fighter=fighter, opponent=opponent, details=fight_details, **validated_data)
        return fight

    def _bulk_create(self, fighter, validated_data_list):
        return_list = []
        for validated_data in validated_data_list:
            return_list.append(self._single_create(fighter, validated_data))
        return return_list

    def create(self, validated_data):
        slug = self._get_slug()
        fighter = Fighter.objects.get(slug=slug)

        if isinstance(validated_data, list):
            return self._bulk_create(fighter, validated_data)
        return self._single_create(fighter, validated_data)
