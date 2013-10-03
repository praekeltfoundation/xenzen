from django.db import models
from django.contrib.auth.models import User


class XenServer(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    memory = models.IntegerField(default=0)
    cores = models.IntegerField(default=0)
    subnet = models.CharField(max_length=255, blank=True)

class XenVM(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=128)
    xsref = models.CharField(max_length=255, unique=True)

    sockets = models.IntegerField()
    memory = models.IntegerField()

    ip = models.CharField(max_length=128, blank=True)

    xenserver = models.ForeignKey(XenServer, null=True)

    
class Template(models.Model):
    name = models.CharField(max_length=255)

    cores = models.IntegerField()
    memory = models.IntegerField()

    iso = models.CharField(max_length=255)

    diskspace = models.IntegerField()
    preseed = models.TextField(blank=True)

