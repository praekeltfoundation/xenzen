# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Zone'
        db.create_table(u'xenserver_zone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'xenserver', ['Zone'])

        # Adding model 'XenServer'
        db.create_table(u'xenserver_xenserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('memory', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('mem_free', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('cpu_util', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('cores', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('subnet', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xenserver.Zone'])),
        ))
        db.send_create_signal(u'xenserver', ['XenServer'])

        # Adding model 'Project'
        db.create_table(u'xenserver_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('max_cores', self.gf('django.db.models.fields.IntegerField')(default=8)),
            ('max_memory', self.gf('django.db.models.fields.IntegerField')(default=16384)),
        ))
        db.send_create_signal(u'xenserver', ['Project'])

        # Adding M2M table for field administrators on 'Project'
        m2m_table_name = db.shorten_name(u'xenserver_project_administrators')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'xenserver.project'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'user_id'])

        # Adding model 'XenVM'
        db.create_table(u'xenserver_xenvm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('xsref', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sockets', self.gf('django.db.models.fields.IntegerField')()),
            ('memory', self.gf('django.db.models.fields.IntegerField')()),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('xenserver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xenserver.XenServer'], null=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xenserver.Project'], null=True)),
        ))
        db.send_create_signal(u'xenserver', ['XenVM'])

        # Adding model 'XenMetrics'
        db.create_table(u'xenserver_xenmetrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xenserver.XenVM'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('timeblob', self.gf('django.db.models.fields.TextField')()),
            ('datablob', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'xenserver', ['XenMetrics'])

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

        # Adding model 'AuditLog'
        db.create_table(u'xenserver_auditlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('severity', self.gf('django.db.models.fields.IntegerField')()),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'xenserver', ['AuditLog'])


    def backwards(self, orm):
        # Deleting model 'Zone'
        db.delete_table(u'xenserver_zone')

        # Deleting model 'XenServer'
        db.delete_table(u'xenserver_xenserver')

        # Deleting model 'Project'
        db.delete_table(u'xenserver_project')

        # Removing M2M table for field administrators on 'Project'
        db.delete_table(db.shorten_name(u'xenserver_project_administrators'))

        # Deleting model 'XenVM'
        db.delete_table(u'xenserver_xenvm')

        # Deleting model 'XenMetrics'
        db.delete_table(u'xenserver_xenmetrics')

        # Deleting model 'Template'
        db.delete_table(u'xenserver_template')

        # Deleting model 'AuditLog'
        db.delete_table(u'xenserver_auditlog')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'subnet': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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