from rapidsms.tests.harness import RapidTest
from textpoll import models as textpoll


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
        "User should recieve a message if there are no active polls."
        connection = self.create_connection(data={'backend': self.backend})
        self.receive("poll vote test", connection)
        self.assertEqual(1, len(self.outbound))
        self.assertTrue("polls are closed" in self.outbound[0].text)

    def test_vote(self):
        "Make sure voting is recorded properly with correct answers."
        poll = self.create_sample_poll()
        connection = self.create_connection(data={'backend': self.backend})
        vote = poll.options.all()[0].text
        self.receive("poll vote %s" % vote, connection)
        self.assertEqual(poll.votes.all()[0].connection.pk, connection.pk)
        self.assertTrue("Thank you" in self.outbound[0].text)

    def test_invalid_vote(self):
        "Only proper votes will get stored."
        poll = self.create_sample_poll()
        connection = self.create_connection(data={'backend': self.backend})
        self.receive("poll vote invalid", connection)
        self.assertEqual(0, poll.votes.count())
        self.assertTrue("is not a valid vote" in self.outbound[0].text)

    def test_double_vote(self):
        "Double votes shouldn't cause any errors."
        poll = self.create_sample_poll()
        connection = self.create_connection(data={'backend': self.backend})
        vote = poll.options.all()[0].text
        self.receive("poll vote %s" % vote, connection)
        self.receive("poll vote %s" % vote, connection)
        self.assertEqual(1, poll.votes.count())
        self.assertTrue("already voted" in self.outbound[1].text)

    def test_double_active_poll(self):
        "There should only ever be one active poll."
        self.create_sample_poll()
        poll2 = self.create_sample_poll()
        self.assertEqual(1, textpoll.Poll.objects.filter(active=True).count())
        self.assertEqual(poll2.pk, textpoll.Poll.objects.get(active=True).pk)
