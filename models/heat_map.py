# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: Heatmap Models
"""
from tortoise import fields
from tortoise.models import Model

# class TimestampMixin(Model):
#     create_time = fields.DatetimeField(auto_now_add=True, description='created at')
#     update_time = fields.DatetimeField(auto_now=True, description="updated at")

#     class Meta:
#         abstract = True
        
class Heatmap(Model):
    nama = fields.CharField(default='', max_length=255, description='nama')
    d = fields.CharField(default='', max_length=500, description='d')
    floor = fields.CharField(default='', max_length=255, description='floor')

    
    class Meta:
        table_description = "Heatmap Table"
        table = "heat_map"
