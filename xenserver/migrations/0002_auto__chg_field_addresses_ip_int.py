# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Addresses.ip_int'
        db.alter_column(u'xenserver_addresses', 'ip_int', self.gf('django.db.models.fields.BigIntegerField')())

    def backwards(self, orm):

        # Changing field 'Addresses.ip_int'
        db.alter_column(u'xenserver_addresses', 'ip_int', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'xenserver.addresses': {
            'Meta': {'object_name': 'Addresses'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ip_int': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.AddressPool']"}),
            'version': ('django.db.models.fields.IntegerField', [], {}),
            'vm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.XenVM']", 'null': 'True', 'blank': 'True'})
        },
        u'xenserver.addresspool': {
            'Meta': {'object_name': 'AddressPool'},
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.XenServer']", 'null': 'True', 'blank': 'True'}),
            'subnet': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'version': ('django.db.models.fields.IntegerField', [], {}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.Zone']"})
        },
        u'xenserver.auditlog': {
            'Meta': {'object_name': 'AuditLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'severity': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'xenserver.project': {
            'Meta': {'object_name': 'Project'},
            'administrators': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_cores': ('django.db.models.fields.IntegerField', [], {'default': '8'}),
            'max_memory': ('django.db.models.fields.IntegerField', [], {'default': '16384'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
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
        u'xenserver.xenmetrics': {
            'Meta': {'object_name': 'XenMetrics'},
            'datablob': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timeblob': ('django.db.models.fields.TextField', [], {}),
            'vm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.XenVM']"})
        },
        u'xenserver.xenserver': {
            'Meta': {'object_name': 'XenServer'},
            'cores': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'cpu_util': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mem_free': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'memory': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.Zone']"})
        },
        u'xenserver.xenvm': {
            'Meta': {'object_name': 'XenVM'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'memory': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.Project']", 'null': 'True'}),
            'sockets': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'xenserver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xenserver.XenServer']", 'null': 'True'}),
            'xsref': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'xenserver.zone': {
            'Meta': {'object_name': 'Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['xenserver']