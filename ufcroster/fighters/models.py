from autoslug import AutoSlugField
from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils import FieldTracker
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.placeholder import OnStoragePlaceholderImage

from common.models import TimeStampedModel
from common.utils import get_image_data
from events.models import Event
from .managers import FightDetailsManager, FightQuerySet, FighterManagerWithQueryset


def fighter_images_directory_path(instance, filename):
    if isinstance(instance, Fighter):
        fighter_id = instance.id
    else:
        fighter_id = instance.fighter_id

    return f'fighters/{fighter_id}/{instance.id}{filename}'


class Fighter(TimeStampedModel):
    FEMALE = 'F'
    MALE = 'M'

    GENDER = (
        (FEMALE, _('Female')),
        (MALE, _('Male')),
    )

    name = models.CharField(_('Full name'), max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    nickname = models.CharField(_('Nickname'), max_length=255, blank=True, null=True)
    birthdate = models.DateField(_('Birthdate'), blank=True, null=True)
    birthplace = models.CharField(_('Brith place'), max_length=50, blank=True)
    country = CountryField(blank=True, null=True, default=None, db_index=True)
    nationality = models.CharField(_('Nationality'), max_length=20, blank=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER)

    height = models.CharField(_('Height'), max_length=6, blank=True)
    height_imp = models.CharField(_('Height imperial'), max_length=6, blank=True)

    weight = models.CharField(_('Weight'), max_length=6, blank=True)
    weight_imp = models.CharField(_('Weight imperial'), max_length=6, blank=True)
    weight_class = models.CharField(_('Weight class'), max_length=100, blank=True)

    reach = models.CharField(_('Reach'), max_length=6, blank=True)

    team = models.CharField(_('Team'), max_length=50, blank=True)

    image = VersatileImageField(upload_to=fighter_images_directory_path, blank=True,
                                placeholder_image=OnStoragePlaceholderImage(path='fighters/placeholder.png'))

    ufc_id = models.PositiveIntegerField(blank=True, null=True, default=None)
    rank = models.IntegerField(blank=True, null=True)
    in_ufc = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    objects = FighterManagerWithQueryset()

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.active:
            return reverse('fighters:detail', kwargs={'slug': self.slug})
        return self.urls.sherdog

    def create_urls(self, **urls):
        FighterUrls.objects.create(fighter=self, **urls)

    def create_record(self, **record):
        FighterRecord.objects.create(fighter=self, **record)

    def get_fight_ordinal(self, fight, is_db_updated=False):
        if is_db_updated and fight.is_upcoming():
            return self.fights.filter(details__type=FightDetails.PROFESSIONAL).count() + 1
        return self.fights.filter(details=fight.details).values_list('ordinal', flat=True).first()

    def upcoming_fight(self):
        return self.fights.fight_with_relations().filter(details__status=FightDetails.UPCOMING).first()

    @property
    def last_5_results(self):
        results = self.fights.filter(details__status=FightDetails.PAST,
                                     details__type=FightDetails.PROFESSIONAL).values_list('result', flat=True)
        return ','.join(results[:5])

    def add_image(self, url):
        image = FighterImage(fighter=self)
        image.image.save(*get_image_data(url), save=False)
        image.save()

    def pro_fights_count(self):
        return self.fights.filter(details__type=FightDetails.PROFESSIONAL).count()

    def pro_record(self):
        return self.fights.filter(details__type=FightDetails.PROFESSIONAL).aggregate(
            wins=Sum(Case(When(result=Fight.WIN, then=1), output_field=IntegerField(), default=0)),
            losses=Sum(Case(When(result=Fight.LOSS, then=1), output_field=IntegerField(), default=0)),
            draws=Sum(Case(When(result=Fight.DRAW, then=1), output_field=IntegerField(), default=0)),
            nc=Sum(Case(When(result=Fight.NOCONTEST, then=1), output_field=IntegerField(), default=0)),

            wins_ko_tko=Sum(Case(When(details__method_type=FightDetails.KO_TKO, result=Fight.WIN, then=1),
                                 output_field=IntegerField(), default=0)),
            wins_sub=Sum(Case(When(details__method_type=FightDetails.SUBMISSION, result=Fight.WIN, then=1),
                              output_field=IntegerField(), default=0)),
            wins_dec=Sum(Case(When(details__method_type=FightDetails.DECISION, result=Fight.WIN, then=1),
                              output_field=IntegerField(), default=0)),
            wins_other=Sum(Case(When(details__method_type=FightDetails.OTHER, result=Fight.WIN, then=1),
                                output_field=IntegerField(), default=0)),

            losses_ko_tko=Sum(Case(When(details__method_type=FightDetails.KO_TKO, result=Fight.LOSS, then=1),
                                   output_field=IntegerField(), default=0)),
            losses_sub=Sum(Case(When(details__method_type=FightDetails.SUBMISSION, result=Fight.LOSS, then=1),
                                output_field=IntegerField(), default=0)),
            losses_dec=Sum(Case(When(details__method_type=FightDetails.DECISION, result=Fight.LOSS, then=1),
                                output_field=IntegerField(), default=0)),
            losses_other=Sum(Case(When(details__method_type=FightDetails.OTHER, result=Fight.LOSS, then=1),
                                  output_field=IntegerField(), default=0)),

            # draws_f=Sum(Case(When(details__method_type=FightDetails.DRAW, then=1), output_field=IntegerField(),
            #                  default=0)),
            #
            # nc_f=Sum(Case(When(details__method_type=FightDetails.NC, then=1), output_field=IntegerField(),
            #               default=0)),
        )


class FighterRecord(TimeStampedModel):
    fighter = models.OneToOneField(Fighter, related_name='record', on_delete=models.CASCADE)
    total = models.CharField(max_length=48, blank=True, null=True, default=None)
    last_5 = models.CharField(max_length=20, blank=True, default='')

    wins = models.IntegerField(blank=True, null=True, default=0)
    losses = models.IntegerField(blank=True, null=True, default=0)
    draws = models.IntegerField(blank=True, null=True, default=0)
    nc = models.IntegerField(blank=True, null=True, default=0)

    wins_ko_tko = models.IntegerField(blank=True, null=True, default=0)
    wins_sub = models.IntegerField(blank=True, null=True, default=0)
    wins_dec = models.IntegerField(blank=True, null=True, default=0)
    wins_other = models.IntegerField(blank=True, null=True, default=0)

    losses_ko_tko = models.IntegerField(blank=True, null=True, default=0)
    losses_sub = models.IntegerField(blank=True, null=True, default=0)
    losses_dec = models.IntegerField(blank=True, null=True, default=0)
    losses_other = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f'{self.fighter.name} {self.total}'

    def save(self, *args, **kwargs):
        self.total = self.get_total()
        self.last_5 = self.fighter.last_5_results
        super().save(*args, **kwargs)

    @property
    def last_5_list(self):
        if self.last_5:
            return self.last_5.split(',')
        return []

    def get_total(self):
        record = f'{self.wins} - {self.losses} - {self.draws}'
        if self.nc:
            record = f'{record}, {self.nc}NC'
        return record

    def is_consistent(self):
        wins_sum = self.wins_ko_tko + self.wins_sub + self.wins_dec + self.wins_other
        losses_sum = self.losses_ko_tko + self.losses_sub + self.losses_dec + self.losses_other

        if self.wins == wins_sum and self.losses == losses_sum:
            return True
        return False

    @property
    def total_fights(self):
        return self.wins + self.losses + self.draws + self.nc


class FighterUrls(TimeStampedModel):
    fighter = models.OneToOneField(Fighter, related_name='urls', on_delete=models.CASCADE)

    ufc = models.URLField(max_length=100, blank=True, null=True, unique=True)
    sherdog = models.URLField(max_length=100, blank=True, null=True, unique=True)
    wiki = models.URLField(max_length=100, blank=True)
    website = models.URLField(max_length=100, blank=True)

    facebook = models.URLField(max_length=100, blank=True)
    instagram = models.URLField(max_length=100, blank=True)
    youtube = models.URLField(max_length=100, blank=True)
    twitter = models.URLField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'Fighter urls'

    @property
    def display_list(self):
        display_list = [
            ('ufc', 'UFC'),
            ('sherdog', 'SHERDOG'),
            ('wiki', 'WIKI'),
            ('website', 'WWW'),
            ('instagram', '<i class="fa fa-lg fa-instagram" aria-hidden="true"></i>'),
            ('facebook', '<i class="fa fa-lg fa-facebook" aria-hidden="true"></i>'),
            ('youtube', '<i class="fa fa-lg fa-youtube-play" aria-hidden="true"></i>'),
            ('twitter', '<i class="fa fa-lg fa-twitter" aria-hidden="true"></i>')
        ]
        for field_name, display in display_list:
            url_ = getattr(self, field_name)
            if url_:
                yield (url_, display)


class FighterImage(TimeStampedModel):
    fighter = models.ForeignKey(Fighter, related_name='images')
    image = VersatileImageField(upload_to=fighter_images_directory_path, blank=True,
                                placeholder_image=OnStoragePlaceholderImage(path='fighters/placeholder.png'))

    class Meta:
        ordering = ['-created']


class FightDetails(TimeStampedModel):
    AMATEUR = 'A'
    EXHIBITION = 'E'
    PROFESSIONAL = 'P'

    FIGHT_TYPES = (
        (AMATEUR, _('Amateur')),
        (EXHIBITION, _('Exhibition fight')),
        (PROFESSIONAL, _('Professional'))
    )

    KO_TKO = 'KO/TKO'
    SUBMISSION = 'SUBMISSION'
    DECISION = 'DECISION'
    OTHER = 'OTHER'
    NC = 'NC'
    DRAW = 'DRAW'

    METHOD_TYPES = (
        (KO_TKO, 'KO/TKO'),
        (SUBMISSION, 'SUBMISSION'),
        (DECISION, 'DECISION'),
        (OTHER, 'OTHER'),
        (NC, 'NC'),
        (DRAW, 'DRAW')
    )

    UPCOMING = 'U'
    PAST = 'P'

    STATUS = (
        (UPCOMING, _('Upcoming')),
        (PAST, _('Past'))
    )

    event = models.ForeignKey(Event, related_name='fights', blank=True, null=True, on_delete=models.CASCADE)

    status = models.CharField(max_length=1, choices=STATUS, null=True, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=FIGHT_TYPES, blank=True)
    method = models.CharField(max_length=128, blank=True)
    method_type = models.CharField(max_length=15, choices=METHOD_TYPES, blank=True, null=True, default=None)
    round = models.CharField(max_length=2, blank=True)
    time = models.CharField(max_length=5, blank=True)
    referee = models.CharField(max_length=255, blank=True)
    ordinal = models.IntegerField(blank=True, null=True, default=None)

    tracker = FieldTracker(fields=['event', 'status', 'date'])

    objects = FightDetailsManager()

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Fight details'

    def __str__(self):
        return f'{self.pk} {self.date} {self.status} {self.type}'

    @property
    def method_display(self):
        return self.method.replace(' ', '\n', 1)


class Fight(TimeStampedModel):
    WIN = 'W'
    LOSS = 'L'
    DRAW = 'D'
    NOCONTEST = 'NC'

    RESULTS = (
        (WIN, _('Win')),
        (LOSS, _('Loss')),
        (DRAW, _('Draw')),
        (NOCONTEST, _('No contest')),
    )

    details = models.ForeignKey(FightDetails, related_name='fights', on_delete=models.CASCADE)
    fighter = models.ForeignKey(Fighter, related_name='fights', on_delete=models.CASCADE)
    opponent = models.ForeignKey(Fighter, null=True, on_delete=models.CASCADE)

    opponent_last_5 = models.CharField(max_length=20, blank=True)
    opponent_record_before = models.CharField(max_length=20, blank=True)
    result = models.CharField(max_length=2, choices=RESULTS, blank=True)
    ordinal = models.IntegerField(blank=True, null=True)

    tracker = FieldTracker(fields=['opponent', 'result'])

    objects = FightQuerySet.as_manager()

    class Meta:
        unique_together = ('details', 'fighter', 'opponent')
        ordering = ['-details__date', '-ordinal']

    def __str__(self):
        return f'{self.fighter.name} {self.get_result_display()} {self.opponent.name}'

    def add_fight_to_record(self, method_type):
        record = self.fighter.record
        record_result_map = {self.WIN: 'wins', self.LOSS: 'losses', self.DRAW: 'draws', self.NOCONTEST: 'nc'}
        record_method_map = {
            self.LOSS: {
                FightDetails.KO_TKO: 'losses_ko_tko',
                FightDetails.SUBMISSION: 'losses_sub',
                FightDetails.DECISION: 'losses_dec',
                FightDetails.OTHER: 'losses_other'
            },
            self.WIN: {
                FightDetails.KO_TKO: 'wins_ko_tko',
                FightDetails.SUBMISSION: 'wins_sub',
                FightDetails.DECISION: 'wins_dec',
                FightDetails.OTHER: 'wins_other'
            }
        }

        record_result_field = record_result_map.get(self.result)
        record_method_field = record_method_map.get(self.result, {}).get(method_type)

        if record_result_field:
            result_count = getattr(record, record_result_field)
            setattr(record, record_result_field, result_count + 1)

        if record_method_field:
            method_count = getattr(record, record_method_field)
            setattr(record, record_method_field, method_count + 1)

        record.save()

    @property
    def opponent_last_5_list(self):
        if self.opponent_last_5:
            return self.opponent_last_5.split(',')
        return []

    @property
    def was_previously_upcoming(self):
        previous_status = self.details.tracker.previous('status')
        if previous_status == FightDetails.UPCOMING and self.is_past():
            return True
        return False

    def is_upcoming(self):
        return self.details.status == FightDetails.UPCOMING

    def is_past(self):
        return self.details.status == FightDetails.PAST
