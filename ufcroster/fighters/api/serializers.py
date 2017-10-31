from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from ..models import Fighter, FighterUrls, FighterRecord


class FighterUrlsSerializer(ModelSerializer):
    class Meta:
        model = FighterUrls
        exclude = ('id', 'fighter')


class FighterRecordSerializer(ModelSerializer):
    class Meta:
        model = FighterRecord
        exclude = ('id', 'fighter')


class FighterSerializer(HyperlinkedModelSerializer):
    urls = FighterUrlsSerializer()
    record = FighterRecordSerializer()

    class Meta:
        model = Fighter
        fields = '__all__'
        extra_fields = ('urls', 'record')
        extra_kwargs = {
            'url': {'view_name': 'api:fighter-detail', 'lookup_field': 'slug'}
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
        urls = validated_data.pop('urls')
        record = validated_data.pop('record')
        fighter = super().update(instance, validated_data)
        FighterUrlsSerializer().update(fighter.urls, urls)
        FighterRecordSerializer().update(fighter.record, record)
        return fighter
