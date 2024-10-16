# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: WorkflowEditor Models
"""
from tortoise import fields
from tortoise.models import Model

class TimestampMixin(Model):
    create_time = fields.DatetimeField(auto_now_add=True, description='created at')
    update_time = fields.DatetimeField(auto_now=True, description="updated at")

    class Meta:
        abstract = True
        
class WorkflowEditor(TimestampMixin):
    name = fields.CharField(default='', max_length=255, description='name')
    nodesjson = fields.JSONField(default=[])
    edgesjson = fields.JSONField(default=[])

    
    class Meta:
        table_description = "WorkflowEditor Table"
        table = "workfloweditor"
