# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'XenServer'
        db.create_table(u'xenserver_xenserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('memory', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cores', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('subnet', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'xenserver', ['XenServer'])

        # Adding model 'XenVM'
        db.create_table(u'xenserver_xenvm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('xsref', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('sockets', self.gf('django.db.models.fields.IntegerField')()),
            ('memory', self.gf('django.db.models.fields.IntegerField')()),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('xenserver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xenserver.XenServer'], null=True)),
        ))
        db.send_create_signal(u'xenserver', ['XenVM'])

        # Adding model 'Template'
        db.create_table(u'xenserver_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('cores', self.gf('django.db.models.fields.IntegerField')()),
            ('memory', self.gf('django.db.models.fields.IntegerField')()),
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('diskspace', self.gf('django.db.models.fields.IntegerField')()),
            ('preseed', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'xenserver', ['Template'])


    def backwards(self, orm):
        # Deleting model 'XenServer'
        db.delete_table(u'xenserver_xenserver')

        # Deleting model 'XenVM'
        db.delete_table(u'xenserver_xenvm')

        # Deleting model 'Template'
        db.delete_table(u'xenserver_template')


    models = {
        u'xenserver.template': {
            'Meta': {'object_name': 'Template'},
            'cores': ('django.db.models.fields.IntegerField', [], {}),
            'diskspace': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'memory': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'preseed': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'xenserver.xenserver': {
            'Meta': {'object_name': 'XenServer'},
            'cores': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'subnet': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'xenserver.xenvm': {
            'Meta': {'object_name': 'XenVM'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'memory': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sockets': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'xenserver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.XenServer']", 'null': 'True'}),
            'xsref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['xenserver']