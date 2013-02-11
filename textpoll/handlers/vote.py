from __future__ import unicode_literals

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from textpoll.handlers.base import PollHandler
from textpoll.forms import VoteForm


class VoteHandler(PollHandler):
    "Records vote for a poll."

    keyword = 'vote'
    form = VoteForm
    success_text = _('Thank you!')
    help_text = _('To vote, send: %(prefix)s %(keyword)s.')

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        result['text'] = tokens.pop(0)
        return result

    def __handle(self, text):
        "Register user with a given timeline based on the keyword match."
        parsed = self.parse_message(text)
        form = VoteForm(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            form.save()
        return True
