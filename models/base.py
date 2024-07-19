# -*- coding:utf-8 -*-
"""
@Time : 2022/4/24 10:40 AM
@Maintainer: dgos
@Des: 基础模型
"""

from tortoise import fields
from tortoise.models import Model

from datetime import datetime

class TimestampMixin(Model):
    create_time = fields.DatetimeField(default=datetime.now(), description='created at')
    update_time = fields.DatetimeField(auto_now=True, description="Updated at")

    class Meta:
        abstract = True



class User(TimestampMixin):
    role: fields.ManyToManyRelation["Role"] = \
        fields.ManyToManyField("base.Role", related_name="user", on_delete=fields.CASCADE)
    username = fields.CharField(null=True, max_length=25)
    user_type = fields.BooleanField(default=False, description="True: SuperAdministrator False: Ordinary Administrator")
    password = fields.CharField(null=True, max_length=255)
    nickname = fields.CharField(default='', max_length=255)
    user_phone = fields.CharField(null=True, max_length=11)
    user_email = fields.CharField(null=True, max_length=255)
    full_name = fields.CharField(null=True, max_length=255)
    user_status = fields.IntField(default=0, description='0 No activation 1 Normal 2 Disable')
    header_img = fields.CharField(null=True, max_length=255, description='avatar')
    sex = fields.IntField(default=0, null=True, description='0 Unknown 1 Men and 2 Women')
    remarks = fields.CharField(null=True, max_length=30, description="Remark")
    client_host = fields.CharField(null=True, max_length=19, description="Access IP")

    class Meta:
        table_description = "User Table"
        table = "user"


class Role(TimestampMixin):
    user: fields.ManyToManyRelation[User]
    role_name = fields.CharField(max_length=25, description="Role Name")
    access: fields.ManyToManyRelation["Access"] = \
        fields.ManyToManyField("base.Access", related_name="role", on_delete=fields.CASCADE)
    role_status = fields.BooleanField(default=False, description="True: Enable False: Disable")
    role_desc = fields.CharField(null=True, max_length=255, description='Character description')

    class Meta:
        table_description = "Character table"
        table = "role"


class Access(TimestampMixin):
    role: fields.ManyToManyRelation[Role]
    access_name = fields.CharField(max_length=15, description="Permission name")
    parent_id = fields.IntField(default=0, description='ParentID')
    scopes = fields.CharField(unique=True, max_length=255, description='Permanent scope identification')
    access_desc = fields.CharField(null=True, max_length=255, description='Permissions description')
    menu_icon = fields.CharField(null=True, max_length=255, description='Menu icon')
    is_check = fields.BooleanField(default=False, description='Whether to verify the permissions TRUE to verify that FALSE does not verify')
    is_menu = fields.BooleanField(default=False, description='Whether it is the menu TRUE menu FALSE is not the menu')

    class Meta:
        table_description = "Permissions table"
        table = "access"


class AccessLog(TimestampMixin):
    user_id = fields.IntField(description="用户ID")
    target_url = fields.CharField(null=True, description="访问的url", max_length=255)
    user_agent = fields.CharField(null=True, description="访问UA", max_length=255)
    request_params = fields.JSONField(null=True, description="请求参数get|post")
    ip = fields.CharField(null=True, max_length=32, description="访问IP")
    note = fields.CharField(null=True, max_length=255, description="备注")

    class Meta:
        table_description = "用户操作记录表"
        table = "access_log"


class SystemParams(TimestampMixin):
    params_name = fields.CharField(unique=True, max_length=255, description="参数名")
    params = fields.JSONField(description="参数")

    class Meta:
        table_description = "系统参数表"
        table = "system_params"
