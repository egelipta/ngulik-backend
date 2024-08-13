# -*- coding:utf-8 -*-
"""
@Time : 2023/12/27 11:59 PM
@Author: elge
@Des: RackServer Extends
"""

import datetime
from typing import Any, Dict, List, Optional
from core.Response import success, fail, res_antd
from models.rack_server import RackServer
from schemas import rack_server
from fastapi import HTTPException, Request, Query, APIRouter
from tortoise.queryset import F

router = APIRouter(prefix='/rack_server')

@router.get("",
            summary="RackServer List",
            response_model=rack_server.RackServerListData,
            # dependencies=[Security(check_permissions, scopes=["rack_server_query"])]
            )
async def rack_server_list(
        pageSize: int = 10,
        current: int = 1,
        name: str = Query(None),
        width: int = Query(None),
        height: int = Query(None),
        depth: int = Query(None),
        x: int = Query(None),
        y: int = Query(None),
        z: int = Query(None),
        create_time: str = Query(None),
        update_time: str = Query(None),

):
    """
    Get All RackServers
    :return:
    """
    # Query Conditions
    query = {}
    if name:
        query.setdefault('name__icontains', name)
    if width:
        query.setdefault('width__icontains', width)
    if height:
        query.setdefault('height__icontains', height)
    if depth:
        query.setdefault('depth__icontains', depth)
    if x:
        query.setdefault('x__icontains', x)
    if y:
        query.setdefault('y__icontains', y)
    if z:
        query.setdefault('z__icontains', z)
    if create_time:
        query.setdefault('create_time__range', create_time)
    if update_time:
        query.setdefault('update_time__range', update_time)

    rack_server_data = RackServer.annotate(key=F("id")).filter(**query).all()
    # Total
    total = await rack_server_data.count()
    # Query
    data = await rack_server_data.limit(pageSize).offset(pageSize * (current - 1)).order_by("-create_time") \
        .values(
        "key", "id", "name", "width", "height", "depth", "x", "y", "z" ,"create_time", "update_time")

    return res_antd(code=True, data=data, total=total)



@router.post("", summary="Rack Server Add",
# dependencies=[Security(check_permissions, scopes=["tugas_add"])]
)
async def rack_server_add(post: rack_server.CreateRackServer):
    """
    Tugas Add
    :param post: CreateTugas
    :return:
    """
    # Filter Rack Server
    # get_posisi_rack = await RackServer.get_or_none(x=post.x)
    # if get_posisi_rack:
    #     return fail(msg="Posisi sudah ditempati, pilih posisi lain!")

    create_rack_server = await RackServer.create(**post.dict())
    if not create_rack_server:
        return fail(msg=f"Failed to create Tugas {post.name}!")
    return success(msg=f"{create_rack_server.name} berhasil disimpan")

@router.get("/data-rack-server", summary="Data Rack Server")
async def data_rack_server():
    data = await RackServer.all()
    return data
