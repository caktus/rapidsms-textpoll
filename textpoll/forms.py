from __future__ import unicode_literals

from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from textpoll import models as textpoll


class PlainErrorList(ErrorList):
    "Customization of the error list for including in an SMS message."

    def as_text(self):
        if not self:
            return ''
        return ''.join(['%s' % force_unicode(e) for e in self])


class HandlerForm(forms.Form):
    "Base form class for validating SMS handler message data."

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop('connection', None)
        kwargs['error_class'] = PlainErrorList
        super(HandlerForm, self).__init__(*args, **kwargs)

    def error(self):
        "Condense form errors to single error message."
        errors = self.errors
        error = None
        if self.errors:
            # Return first field error based on field order
            for field in self.fields:
                if field in errors:
                    error = errors[field].as_text()
                    break
            if error is None and NON_FIELD_ERRORS in errors:
                error = self.errors[NON_FIELD_ERRORS].as_text()
        return error

    def save(self):
        "Update necessary data and return parameters for the success message."
        return {}


class VoteForm(HandlerForm):

    text = forms.CharField()

    def __init__(self, *args, **kwargs):
        try:
            self.poll = textpoll.Poll.objects.filter(active=True)[0]
        except IndexError:
            self.poll = None
        super(VoteForm, self).__init__(*args, **kwargs)

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if not self.poll:
            return text
        try:
            option = self.poll.options.filter(text__iexact=text)[0]
        except IndexError:
            options = ", ".join(self.poll.options.values_list('text',
                                                              flat=True))
            message = "%s is not a valid vote. Please choose from %s" % (
                text, options)
            raise forms.ValidationError(message)
        self.cleaned_data['option'] = option
        return text

    def clean(self):
        if not self.poll:
            raise forms.ValidationError(_("Sorry, the polls are closed."))
        if self.poll.votes.filter(connection=self.connection).exists():
            raise forms.ValidationError(_("You already voted."))
        return self.cleaned_data

    def save(self):
        self.poll.votes.create(connection=self.connection, poll=self.poll,
                               option=self.cleaned_data['option'],
                               text=self.cleaned_data['text'])
        return {}
