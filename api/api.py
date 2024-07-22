# -*- coding:utf-8 -*-
"""
@Created on : 2022/4/22 22:02
@Maintainer: dgos
@Des: api路由
"""
from fastapi import APIRouter
from api.endpoints.test import test_oath2
from api.endpoints import user, role, access
from api.extends import tugas, heat_map, rack_server


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user.router, prefix='/admin', tags=["User Management"])
api_router.include_router(role.router, prefix='/admin', tags=["Role management"])
api_router.include_router(access.router, prefix='/admin', tags=["authority management"])
api_router.include_router(tugas.router, prefix='/tugas', tags=["Tugas"])
api_router.include_router(heat_map.router, prefix='/heat_map', tags=["Heat Map"])
api_router.include_router(rack_server.router, prefix='/rack_server', tags=["Rack Server"])
