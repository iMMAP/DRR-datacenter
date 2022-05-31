# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractUser
from django.db.models import signals
from django.conf import settings

from taggit.managers import TaggableManager

from geonode.base.enumerations import COUNTRIES, ORG_ACCRONYM, ORG_NAME_STATUS
from geonode.groups.models import GroupProfile

from account.models import EmailAddress

from .utils import format_address

if 'notification' in settings.INSTALLED_APPS:
    from notification import models as notification

ORG_RECORD_STATUSES = (
    ('enabled', 'Enabled'),
    ('disabled', 'Disabled'),
    ('requested', 'Requested'),
    ('rejected', 'Rejected'),
)
ORG_TYPES = (
    ("Education", "Education"),
    ("Government Int", "Government Int."),
    ("Government", "Government"),
    ("International NGO", "International NGO"),
    ("National NGO", "National NGO"),
    ("Private/NGO", "Private/NGO"),
    ("Red Cross and Red Crescent Movement", "Red Cross and Red Crescent Movement"),
    ("United Nations", "United Nations"),
)
ORG_NAME_STATUSES = (
    ("OCHA", "OCHA"),
    ("Non_OCHA", "Non_OCHA"),
)

class Profile(AbstractUser):

    """Fully featured Geonode user"""

    organization = models.CharField(
        _('Organization Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('name of the responsible organization'))
    profile = models.TextField(_('Profile'), null=True, blank=True, help_text=_('introduce yourself'))
    position = models.CharField(
        _('Position Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('role or position of the responsible person'))
    voice = models.CharField(_('Voice'), max_length=255, blank=True, null=True, help_text=_(
        'telephone number by which individuals can speak to the responsible organization or individual'))
    fax = models.CharField(_('Facsimile'), max_length=255, blank=True, null=True, help_text=_(
        'telephone number of a facsimile machine for the responsible organization or individual'))
    delivery = models.CharField(
        _('Delivery Point'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('physical and email address at which the organization or individual may be contacted'))
    city = models.CharField(
        _('City'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('city of the location'))
    area = models.CharField(
        _('Administrative Area'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('state, province of the location'))
    zipcode = models.CharField(
        _('Postal Code'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('ZIP or other postal code'))
    country = models.CharField(
        choices=COUNTRIES,
        max_length=3,
        blank=True,
        null=True,
        help_text=_('country of the physical address'))
    keywords = TaggableManager(_('keywords'), blank=True, help_text=_(
        'commonly used word(s) or formalised word(s) or phrase(s) used to describe the subject \
            (space or comma-separated'))
    title = models.CharField(
         _('Title'),
        max_length=30,
        blank=True,
        null=True,
        help_text=_('Title'))
    org_acronym = models.CharField(
         _('Organisation acronym'),
        # choices=ORG_ACCRONYM,
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Organisation acronym'))
    org_type = models.CharField(
         _('Organisation Type'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Organisation Type'))
    org_name_status = models.CharField(
         _('Organisation Name Status'),
        # choices=ORG_NAME_STATUS,
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Organisation Name Status'))

    def get_absolute_url(self):
        return reverse('profile_detail', args=[self.username, ])

    def __unicode__(self):
        return u"%s" % (self.username)

    def class_name(value):
        return value.__class__.__name__

    USERNAME_FIELD = 'username'

    def group_list_public(self):
        return GroupProfile.objects.exclude(access="private").filter(groupmember__user=self)

    def group_list_all(self):
        return GroupProfile.objects.filter(groupmember__user=self)

    def keyword_list(self):
        """
        Returns a list of the Profile's keywords.
        """
        return [kw.name for kw in self.keywords.all()]

    @property
    def name_long(self):
        if self.first_name and self.last_name:
            return '%s %s (%s)' % (self.first_name, self.last_name, self.username)
        elif (not self.first_name) and self.last_name:
            return '%s (%s)' % (self.last_name, self.username)
        elif self.first_name and (not self.last_name):
            return '%s (%s)' % (self.first_name, self.username)
        else:
            return self.username

    @property
    def location(self):
        return format_address(self.delivery, self.zipcode, self.city, self.area, self.country)

class Organization(models.Model):
    '''
    User organization reference table.
    '''
    organization = models.CharField(
        _('Organization Name'),
        max_length=255,
        blank=False,
        null=False,
        help_text=_('Name of the organization'))
    org_acronym = models.CharField(
        _('Organisation acronym'),
        max_length=255,
        blank=True,
        null=True,
        # unique=True,
        help_text=_('Organisation acronym, make sure the value is unique, used as natural key'))
    org_type = models.CharField(
        _('Organisation Type'),
        choices=ORG_TYPES,
        default=ORG_TYPES[0][0],
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Organisation type'))
    org_name_status = models.CharField(
        _('Organisation Name Status'),
        max_length=255,
        choices=ORG_NAME_STATUSES,
        default=ORG_NAME_STATUSES[0][0],
        blank=True,
        null=True,
        help_text=_('Organisation name status'))
    record_status = models.CharField(
        _('Record status'), 
        max_length=255,
        choices=ORG_RECORD_STATUSES,
        default=ORG_RECORD_STATUSES[2][0],
        blank=True,
        null=True,
        help_text=_('Designates whether this record should be treated enabled, disabled, '
            'requested (by user through request add organization form), or rejected.'))
    requester_email = models.CharField(
        _('Requester email'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Requester email'))
    requester_organization_website = models.CharField(
        _('Requester organization website'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Requester organization website'))
    requester_first_name = models.CharField(
        _('Requester first name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Requester first name'))
    requester_last_name = models.CharField(
        _('Requester last name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Requester last name'))
    request_reject_reason = models.TextField(
        _('Request reject reason'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('When rejected state the reason here'))
    created_at = models.DateTimeField(
        _('Create date'),
        max_length=255,
        blank=True,
        null=True,
        auto_now_add=True,
        help_text=_('Create date'))
    updated_at = models.DateTimeField(
        _('Update date'),
        max_length=255,
        blank=True,
        null=True,
        auto_now=True,
        help_text=_('Update date'))

    @staticmethod
    def valid_only():
        return Organization.objects\
            .filter(record_status='enabled', org_acronym__isnull=False)\
            .exclude(org_acronym='')\
            .exclude(org_acronym="NULL")


def get_anonymous_user_instance(Profile):
    return Profile(username='AnonymousUser')


def profile_post_save(instance, sender, **kwargs):
    """Make sure the user belongs by default to the anonymous group.
    This will make sure that anonymous permissions will be granted to the new users."""
    from django.contrib.auth.models import Group
    anon_group, created = Group.objects.get_or_create(name='anonymous')
    instance.groups.add(anon_group)
    # keep in sync Profile email address with Account email address
    if instance.email not in [u'', '', None] and not kwargs.get('raw', False):
        EmailAddress.objects.filter(user=instance, primary=True).update(email=instance.email)


def email_post_save(instance, sender, **kw):
    if instance.primary:
        Profile.objects.filter(id=instance.user.pk).update(email=instance.email)


def profile_pre_save(instance, sender, **kw):
    matching_profiles = Profile.objects.filter(id=instance.id)
    if matching_profiles.count() == 0:
        return
    if instance.is_active and not matching_profiles.get().is_active and \
            'notification' in settings.INSTALLED_APPS:
        notification.send([instance, ], "account_active")

signals.pre_save.connect(profile_pre_save, sender=Profile)
signals.post_save.connect(profile_post_save, sender=Profile)
signals.post_save.connect(email_post_save, sender=EmailAddress)
