# -*- coding:utf-8 -*-
"""
@Time : 2024/11/28 11:59 PM
@Author: elge
@Des: HomeAssistant Models
"""
from tortoise import fields
from tortoise.models import Model

class TimestampMixin(Model):
    create_time = fields.DatetimeField(auto_now_add=True, description='created at')
    update_time = fields.DatetimeField(auto_now=True, description="updated at")

    class Meta:
        abstract = True
        
class HomeAssistant(TimestampMixin):
    datachart = fields.JSONField(default=dict)

    
    class Meta:
        table_description = "Home Assistant Table"
        table = "homeassistant"
