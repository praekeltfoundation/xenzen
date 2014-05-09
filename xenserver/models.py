from django.db import models
from django.contrib.auth.models import User


class Zone(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode().encode('utf-8', 'replace')


class XenServer(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    memory = models.IntegerField(default=1)
    mem_free = models.IntegerField(default=1)
    cpu_util = models.IntegerField(default=1)
    cores = models.IntegerField(default=1)
    subnet = models.CharField(max_length=255, blank=True)

    zone = models.ForeignKey(Zone)

    def __unicode__(self):
        return self.hostname

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class Project(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class XenVM(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=128)
    xsref = models.CharField(max_length=255, unique=True)

    sockets = models.IntegerField()
    memory = models.IntegerField()

    ip = models.CharField(max_length=128, blank=True)

    xenserver = models.ForeignKey(XenServer, null=True)

    project = models.ForeignKey(Project, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

    
class Template(models.Model):
    name = models.CharField(max_length=255)

    cores = models.IntegerField()
    memory = models.IntegerField()

    iso = models.CharField(max_length=255)

    diskspace = models.IntegerField()
    preseed = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class AuditLog(models.Model):
    username = models.ForeignKey(User, null=True)

    time = models.DateTimeField(auto_now_add=True)

    severity = models.IntegerField()
    message = models.TextField()
