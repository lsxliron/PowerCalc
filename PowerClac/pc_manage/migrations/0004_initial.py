# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'client'
        db.create_table(u'pc_manage_client', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_password', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_ip', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_port', self.gf('django.db.models.fields.IntegerField')(default=80)),
            ('client_os', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal(u'pc_manage', ['client'])

        # Adding model 'software'
        db.create_table(u'pc_manage_software', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('software_path', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('software_client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pc_manage.client'])),
            ('software_name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'pc_manage', ['software'])

        # Adding model 'matlab_command'
        db.create_table(u'pc_manage_matlab_command', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('command_keyword', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('m_file_path', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('output_path', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pc_manage.client'])),
            ('software_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pc_manage.software'])),
        ))
        db.send_create_signal(u'pc_manage', ['matlab_command'])


    def backwards(self, orm):
        # Deleting model 'client'
        db.delete_table(u'pc_manage_client')

        # Deleting model 'software'
        db.delete_table(u'pc_manage_software')

        # Deleting model 'matlab_command'
        db.delete_table(u'pc_manage_matlab_command')


    models = {
        u'pc_manage.client': {
            'Meta': {'object_name': 'client'},
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'client_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'client_os': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'client_password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'client_port': ('django.db.models.fields.IntegerField', [], {'default': '80'}),
            'client_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pc_manage.matlab_command': {
            'Meta': {'object_name': 'matlab_command'},
            'client_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pc_manage.client']"}),
            'command_keyword': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'm_file_path': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'output_path': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'software_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pc_manage.software']"})
        },
        u'pc_manage.software': {
            'Meta': {'object_name': 'software'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'software_client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pc_manage.client']"}),
            'software_name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'software_path': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['pc_manage']