# -*- coding:utf-8 -*-
"""
@Time : 2022/4/27 5:24 PM
@Author: me
@Des: Device Management
"""
import os
import time

from api.endpoints.common import write_access_log
from core.Response import success, fail, res_antd
from models.device import Device
from schemas import device, systemInfo
from core.Utils import en_password, check_password, random_str
from core.Auth import create_access_token, check_permissions
from fastapi import Request, Query, APIRouter, Security, File, UploadFile
from config import settings
from typing import List
from tortoise.queryset import F


router = APIRouter(prefix='/systemInfo')


# @router.post("", summary="Device Add", dependencies=[Security(check_permissions, scopes=["device_add"])])
# async def device_add(post: device.CreateDevice):
#     """
#     Device Add
#     :param post: CreateDevice
#     :return:
#     """
#     # Filter Devices
#     get_device_name = await Device.get_or_none(name=post.name)
#     get_device_ip_address = await Device.get_or_none(ip_address=post.ip_address)
    
#     if get_device_name:
#         return fail(msg=f"Device name {post.name} is exist!")
#     if get_device_ip_address:
#         return fail(msg=f"Device IP Address {post.ip_address} is exist!")

#     # post.password = en_password(post.password)

#     # Add User
#     create_device = await Device.create(**post.dict())
#     if not create_device:
#         return fail(msg=f"Failed to create Device {post.name}!")
#     return success(msg=f"Device {create_device.name} created successfully")


# @router.delete("", summary="Device Delete", dependencies=[Security(check_permissions, scopes=["device_delete"])])
# async def device_del(req: Request, ids: List[int]):
#     """
#     Device Delete
#     :param req:
#     :return:
#     """
#     for id in ids:
#         delete_action = await Device.filter(pk=id).delete()
#         if not delete_action:
#             return fail(msg=f"Failed to delete {id}!")
    
#     return success(msg="Deleted successfully")


# @router.put("", summary="Update Device", dependencies=[Security(check_permissions, scopes=["device_update"])])
# async def device_update(post: device.UpdateDevice):
#     """
#     Update device information
#     :param post:
#     :return:
#     """
#     device_check = await Device.get_or_none(pk=post.id)
#     if not device_check:
#         return fail(msg="Device does not exist")
#     if device_check.name != post.name:
#         check = await Device.get_or_none(name=post.name)
#         if check:
#             return fail(msg=f"Device name {check.name} exist!")
#     if device_check.ip_address != post.ip_address:
#         check = await Device.get_or_none(ip_address=post.ip_address)
#         if check:
#             return fail(msg=f"Device ip_address {check.ip_address} exist!")

#     data = post.dict()
#     data.pop("id")
#     await Device.filter(pk=post.id).update(**data)
#     return success(msg="Updated!")


@router.get("",
            summary="System Info",
            response_model=systemInfo.SystemInfoList,
            dependencies=[Security(check_permissions, scopes=["about_query"])]
            )
async def system_info(
        pageSize: int = 10,
        current: int = 1,
        software_name: str = Query(None),
        version: str = Query(None),
        system: str = Query(None),
        jdk_version: str = Query(None),
        database_type: str = Query(None),
        database_port: str = Query(None),
        
):
    """
    Get All Devices
    :return:
    """
    # Query Conditions
    query = {}
    if software_name:
        query.setdefault('software_name', software_name)
    if version:
        query.setdefault('version', version)
    if system:
        query.setdefault('system', system)
    if jdk_version:
        query.setdefault('jdk_version', jdk_version)
    if database_type:
        query.setdefault('database_type', database_type)
    if database_port:
        query.setdefault('database_port', database_port)

    system_info = SystemInfo.annotate(key=F("software_name")).filter(**query).all()
    # Total
    total = await system_info.count()
    # Query
    data = await system_info.limit(pageSize).offset(pageSize * (current - 1)).order_by("version") \
        .values(
        "key", "software_name", "version","system", "jdk_version", "database_type",
        "database_port")

    return res_antd(code=True, data=data, total=total)

