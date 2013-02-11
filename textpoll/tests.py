from rapidsms.tests.harness import RapidTest
from textpoll import models as textpoll
from textpoll.forms import VoteForm


class VoteCreateDataMixin(object):

    def create_poll(self, data={}):
        "Create and return a new Poll."
        defaults = {
            'slug': self.random_string(12),
            'text': self.random_string(32),
        }
        defaults.update(data)
        return textpoll.Poll.objects.create(**defaults)

    def create_option(self, data={}):
        "Create and return a new Option."
        defaults = {
            'text': self.random_string(8),
        }
        defaults.update(data)
        return textpoll.Option.objects.create(**defaults)

    def create_vote(self, data={}):
        "Create and return a new Vote."
        defaults = {
            'text': self.random_string(32),
        }
        defaults.update(data)
        return textpoll.Vote.objects.create(**defaults)


class VoteTest(VoteCreateDataMixin, RapidTest):

    apps = ('rapidsms.contrib.handlers', 'textpoll')

    def setUp(self):
        self.backend = self.create_backend(data={'name': 'mockbackend'})

    def create_sample_poll(self):
        poll = self.create_poll(data={'active': True})
        self.create_option(data={'poll': poll})
        self.create_option(data={'poll': poll})
        return poll

    def test_polls_closed(self):
        ""
        connection = self.create_connection(data={'backend': self.backend})
        self.receive("poll vote test", connection)
        self.assertEqual(1, len(self.outbound))
        self.assertTrue("polls are closed" in self.outbound[0].text)

    def test_invalid_vote(self):
        self.create_sample_poll()
        connection = self.create_connection(data={'backend': self.backend})
        self.receive("poll vote invalid", connection)
        self.assertTrue("is not a valid vote" in self.outbound[0].text)

    def test_vote(self):
        poll = self.create_sample_poll()
        connection = self.create_connection(data={'backend': self.backend})
        vote = poll.options.all()[0].text
        self.receive("poll vote %s" % vote, connection)
        self.assertEqual(poll.votes.all()[0].connection.pk, connection.pk)
        self.assertTrue("Thank you" in self.outbound[0].text)
