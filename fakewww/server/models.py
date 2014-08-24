from django.db import models


class Domain(models.Model):
    domain = models.CharField(max_length=255)
    type = models.CharField(max_length=31)

    def __str__(self):
        return self.domain


class Webpage(models.Model):
    domain = models.ForeignKey(Domain)
    path = models.CharField(max_length=2047, blank=True, default='')
    title = models.CharField(max_length=255)
    keywords = models.CharField(max_length=1023)
    description = models.CharField(max_length=1023)
    content = models.TextField()

    def __str__(self):
        return '{}/{}'.format(self.domain.domain, self.path)
