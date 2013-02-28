from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from textpoll.forms import VoteForm


import re

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class VoteHandler(KeywordHandler):
    "Keyword handler for voting"

    keyword = 'vote'
    form = VoteForm
    success_text = _('Thank you for voting')
    help_text = _('To vote, send: vote <choice>.')

    @classmethod
    def _keyword(cls):
        pattern = r"^\s*(?:%s)\s*(?:[\s,;:]+(.+))?$" % (cls.keyword)
        return re.compile(pattern, re.IGNORECASE)

    def help(self):
        "Return help mesage."
        if self.help_text:
            self.respond(self.help_text)
        else:
            self.unknown()

    def unknown(self):
        "Common fallback for unknown errors."
        params = {'keyword': self.keyword}
        self.respond(_('Sorry, we cannot understand that message. '
            'For additional help send: %(keyword)s') % params)

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        result['text'] = tokens.pop(0)
        return result

    def handle(self, text):
        "Register user with a given timeline based on the keyword match."
        parsed = self.parse_message(text)
        form = VoteForm(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            form.save()
            self.respond(self.success_text)
        else:
            key = 'text' if 'text' in form.errors else '__all__'
            try:
                err_msg = form.errors[key][0]
            except (KeyError, IndexError):
                self.unknown()
            else:
                self.respond(err_msg)
        return True
