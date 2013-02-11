from django.db import models
from rapidsms import models as rapidsms


class Poll(models.Model):
    slug = models.SlugField(unique=True)
    text = models.TextField()
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.slug


class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options')
    text = models.CharField(max_length=32)


class Vote(models.Model):
    poll = models.ForeignKey(Poll, related_name='votes')
    connection = models.ForeignKey(rapidsms.Connection, related_name='votes')
    option = models.ForeignKey(Option, related_name='votes')
    text = models.CharField(max_length=32)
    date = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        unique_together = ("poll", "connection")
