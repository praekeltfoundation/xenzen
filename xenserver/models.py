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

    zone = models.ForeignKey(Zone)

    def __unicode__(self):
        return self.hostname

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class Project(models.Model):
    name = models.CharField(max_length=255)

    max_cores = models.IntegerField(default=8)
    max_memory = models.IntegerField(default=16384)

    administrators = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class AddressPool(models.Model):
    subnet = models.CharField(max_length=128, unique=True)
    gateway = models.CharField(max_length=128)
    zone = models.ForeignKey(Zone)
    server = models.ForeignKey(XenServer, null=True, blank=True)
    version = models.IntegerField()

class XenVM(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=128)
    xsref = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255)

    sockets = models.IntegerField()
    memory = models.IntegerField()

    ip = models.CharField(max_length=128, blank=True)

    xenserver = models.ForeignKey(XenServer, null=True)

    project = models.ForeignKey(Project, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class Addresses(models.Model):
    ip = models.CharField(max_length=128)
    ip_int = models.IntegerField(db_index=True)
    version = models.IntegerField()
    vm = models.ForeignKey(XenVM, null=True, blank=True)
    pool = models.ForeignKey(AddressPool)

    def __unicode__(self):
        return self.ip
    def __str__(self):
        return self.__unicode__().encode('utf-8', 'replace')

class XenMetrics(models.Model):
    vm = models.ForeignKey(XenVM)
    key = models.CharField(max_length=128)
    timeblob = models.TextField()
    datablob = models.TextField()
    
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
