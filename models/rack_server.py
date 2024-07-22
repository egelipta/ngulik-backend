# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: RackServer Models
"""

from tortoise import fields
from tortoise.models import Model

class TimestampMixin(Model):
    create_time = fields.DatetimeField(auto_now_add=True, description='created at')
    update_time = fields.DatetimeField(auto_now=True, description="updated at")

    class Meta:
        abstract = True
        
class RackServer(TimestampMixin):
    name = fields.CharField(default='', max_length=255, description='name')
    width = fields.IntField(description='width')
    height = fields.IntField(description='height')
    depth = fields.IntField(description='depth')
    x = fields.IntField(description='x')
    y = fields.IntField(description='y')
    z = fields.IntField(description='z')


    class Meta:
        table_description = "Rack Server Table"
        table = "rack_server"
