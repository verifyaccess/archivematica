# This file is part of Archivematica.
#
# Copyright 2010-2013 Artefactual Systems Inc. <http://artefactual.com>
#
# Archivematica is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Archivematica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.  If not, see <http://www.gnu.org/licenses/>.

from django import forms

from agentarchives.atom.client import CommunicationError
from requests import Timeout, ConnectionError

from components.archival_storage.atom import get_atom_client


class CreateAICForm(forms.Form):
    results = forms.CharField(label=None, required=True, widget=forms.widgets.HiddenInput())


class UploadMetadataOnlyAtomForm(forms.Form):
    slug = forms.CharField(label='Insert slug', required=True, widget=forms.TextInput(attrs={'class': 'span8'}))

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        client = get_atom_client()
        try:
            client.find_parent_id_for_component(slug)
        except (Timeout, ConnectionError) as e:
            raise forms.ValidationError('Connection establishment failed: AtoM server cannot be reached.')
        except CommunicationError as e:
            if '404' in e.message:
                raise forms.ValidationError('Description with slug %(slug)s not found!', code='notfound', params={'slug': slug})
            raise forms.ValidationError('Unknown error: %(error)s', code='error', params={'error': e.message})
        return slug


class ReingestAIPForm(forms.Form):
    METADATA_ONLY = 'metadata'
    OBJECTS = 'objects'
    REINGEST_CHOICES = (
        (METADATA_ONLY, 'Metadata only'),
        (OBJECTS, 'Metadata and objects')
    )
    reingest_type = forms.ChoiceField(choices=REINGEST_CHOICES, widget=forms.RadioSelect, required=True)


class DeleteAIPForm(forms.Form):
    uuid = forms.CharField(label='Please type in the UUID to confirm', required=True, widget=forms.TextInput(attrs={'class': 'xxlarge', 'placeholder': 'UUID'}))
    reason = forms.CharField(label='Reason for deletion', required=True, widget=forms.Textarea(attrs={'class': 'xxlarge', 'rows': '3'}))

    def __init__(self, *args, **kwargs):
        self.uuid = kwargs.pop('uuid', None)
        if self.uuid is None:
            raise ValueError('uuid must be defined')
        super(forms.Form, self).__init__(*args, **kwargs)

    def clean_uuid(self):
        uuid = self.cleaned_data['uuid']
        if self.uuid != uuid:
            raise forms.ValidationError('UUID mismatch')
        return uuid
