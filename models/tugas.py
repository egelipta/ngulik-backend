# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: Tugas Models
"""
from tortoise import fields
from tortoise.models import Model

class TimestampMixin(Model):
    create_time = fields.DatetimeField(auto_now_add=True, description='created at')
    update_time = fields.DatetimeField(auto_now=True, description="updated at")

    class Meta:
        abstract = True
        
class Tugas(TimestampMixin):
    name = fields.CharField(default='', max_length=255, description='name')
    start = fields.DatetimeField(description='start')
    end = fields.DatetimeField(description='end')
    progress = fields.IntField(description='progress')
    tipe = fields.CharField(default='', max_length=255, description='tipe')
    project = fields.CharField(default='', max_length=255, description='project')
    dependencies = fields.CharField(default='', max_length=255, description='dependencies')
    # hidechildren = fields.BooleanField(default=False, description='hidechildren')

    
    class Meta:
        table_description = "Tugas Table"
        table = "tugas"
