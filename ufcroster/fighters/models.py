from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from .managers import FighterQuerySet


class Fighter(models.Model):
    FEMALE = 'F'
    MALE = 'M'

    GENDER = (
        (FEMALE, _('Female')),
        (MALE, _('Male')),
    )

    slug = models.SlugField(unique=True, blank=True)
    name = models.CharField(_('Full name'), max_length=255)
    nickname = models.CharField(_('Nickname'), max_length=255, blank=True)
    birthdate = models.DateField(_('Birthdate'), blank=True, null=True)
    birthplace = models.CharField(_('Brith place'), max_length=50, blank=True)
    nationality = models.CharField(_('Nationality'), max_length=20, blank=True)
    gender = models.CharField(max_length=1, blank=True)

    height = models.CharField(_('Height'), max_length=6, blank=True)
    height_imp = models.CharField(_('Height imperial'), max_length=6, blank=True)

    weight = models.CharField(_('Weight'), max_length=6, blank=True)
    weight_imp = models.CharField(_('Weight imperial'), max_length=6, blank=True)
    weight_class = models.CharField(_('Weight class'), max_length=100, blank=True)

    reach = models.CharField(_('Reach'), max_length=6, blank=True)

    team = models.CharField(_('Team'), max_length=50, blank=True)

    image = models.ImageField(upload_to='fighters', blank=True)

    rank = models.IntegerField(blank=True, null=True)
    in_ufc = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    objects = FighterQuerySet.as_manager()

    class Meta:
        ordering = ['rank']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.active:
            return reverse('fighters:detail', kwargs={'slug': self.slug})
        return self.urls.sherdog


class FighterUrls(models.Model):
    fighter = models.OneToOneField(Fighter, related_name='urls', on_delete=models.CASCADE)

    ufc = models.URLField(max_length=100, blank=True)
    sherdog = models.URLField(max_length=100, blank=True)
    wiki = models.URLField(max_length=100, blank=True)
    website = models.URLField(max_length=100, blank=True)

    facebook = models.URLField(max_length=100, blank=True)
    instagram = models.URLField(max_length=100, blank=True)
    youtube = models.URLField(max_length=100, blank=True)
    twitter = models.URLField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'FighterUrls'
